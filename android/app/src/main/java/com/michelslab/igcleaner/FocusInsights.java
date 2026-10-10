package com.michelslab.igcleaner;

import android.content.Context;
import android.text.format.DateFormat;

import org.json.JSONObject;

import java.util.ArrayList;
import java.util.Date;
import java.util.List;
import java.util.Locale;
import java.util.Map;

/**
 * One source of truth for native Focus context, including frozen Desktop
 * context, the newest synchronized relationship snapshots and review history.
 * Unknown dates/relationships are never manufactured or treated as proof.
 */
final class FocusInsights {
    private FocusInsights() {}

    static long timestamp(JSONObject value) {
        return value == null ? 0L : validSeconds(value.optLong("timestamp", 0L));
    }

    static long validSeconds(long value) {
        if (value <= 0L) return 0L;
        if (value > 100000000000L) value /= 1000L;
        long now = System.currentTimeMillis() / 1000L;
        return value > now + 86400L ? 0L : value;
    }

    static String date(Context ctx, long seconds) {
        long ts = validSeconds(seconds);
        if (ts <= 0L) return "Sin fecha";
        long days = Math.max(0L, (System.currentTimeMillis() / 1000L - ts) / 86400L);
        String relative;
        if (days == 0L) relative = "hoy";
        else if (days == 1L) relative = "hace 1 día";
        else if (days < 30L) relative = "hace " + days + " días";
        else if (days < 365L) relative = "hace " + Math.max(1L, days / 30L) + " meses";
        else relative = "hace " + (days / 365L) + " años";
        return DateFormat.getMediumDateFormat(ctx).format(new Date(ts * 1000L)) +
                " · " + relative;
    }

    private static String dateTime(Context ctx, String iso) {
        if (iso == null || iso.isBlank()) return "Sin fecha";
        try {
            Date value = Date.from(java.time.Instant.parse(iso));
            return DateFormat.getMediumDateFormat(ctx).format(value) +
                    " · " + DateFormat.getTimeFormat(ctx).format(value);
        } catch (Exception ignored) { return "Sin fecha"; }
    }

    private static String dateTimeMillis(Context ctx, long milliseconds) {
        if (milliseconds <= 0L) return "Sin fecha";
        long ms = milliseconds < 100000000000L ? milliseconds * 1000L : milliseconds;
        Date value = new Date(ms);
        return DateFormat.getMediumDateFormat(ctx).format(value) +
                " · " + DateFormat.getTimeFormat(ctx).format(value);
    }

    private static String order(long following, long follower) {
        if (following <= 0L || follower <= 0L) return "";
        if (following == follower) return "Se siguieron al mismo tiempo";
        long days = Math.abs(following - follower) / 86400L;
        long hours = Math.abs(following - follower) / 3600L;
        String difference = days > 0L ? days + (days == 1L ? " día" : " días")
                : hours > 0L ? hours + (hours == 1L ? " hora" : " horas") : "menos de una hora";
        return (following < follower ? "Tú lo seguiste primero" : "Te siguió primero") +
                " · diferencia de " + difference;
    }

    static String detail(Context ctx, JSONObject item, String module,
                         Map<String, JSONObject> following,
                         Map<String, JSONObject> followers,
                         Map<String, JSONObject> pending,
                         JSONObject workspaceState) {
        if (item == null) return "Sin datos de perfil";
        String user = item.optString("username", "").toLowerCase(Locale.ROOT);
        JSONObject rawContext = item.optJSONObject("context");
        JSONObject row = rawContext == null ? null : rawContext.optJSONObject("row");
        JSONObject followingRecord = following.get(user);
        JSONObject followerRecord = followers.get(user);
        JSONObject pendingRecord = pending.get(user);
        long followingAt = timestamp(followingRecord);
        long followerAt = timestamp(followerRecord);
        long requestAt = timestamp(pendingRecord);

        // Older frozen Desktop batches already embed relationship dates even if
        // a newer snapshot no longer contains the profile.
        if (row != null) {
            boolean main = "main".equals(module) || "review".equals(module);
            if (followingAt == 0L) followingAt = validSeconds(row.optLong(main ? "dateMain" : "dateOther", 0L));
            if (followerAt == 0L) followerAt = validSeconds(row.optLong(main ? "dateOther" : "dateMain", 0L));
            if (requestAt == 0L && "pending".equals(module))
                requestAt = validSeconds(row.optLong("dateMain", 0L));
        }
        List<String> lines = new ArrayList<>();
        if ("pending".equals(module)) {
            lines.add("Solicitud enviada: " + date(ctx, requestAt));
        } else {
            lines.add("Lo seguiste: " + date(ctx, followingAt));
            lines.add("Te siguió: " + date(ctx, followerAt));
            String sequence = order(followingAt, followerAt);
            if (!sequence.isBlank()) lines.add(sequence);
            if (followingRecord != null && followerRecord != null) lines.add("Relación: mutual (según listas sincronizadas)");
            else if (followingRecord != null) {
                JSONObject evidence = workspaceState == null ? null : workspaceState.optJSONObject("followersEvidence");
                if (evidence != null && evidence.optBoolean("partial", false))
                    lines.add("Relación: NO VERIFICABLE · ausencia en HTML parcial");
                else lines.add("Relación: no aparece entre tus followers sincronizados");
            }
            else if (followerRecord != null) lines.add("Relación: follower (según listas sincronizadas)");
            else lines.add("Relación actual: no verificable con los datos disponibles");
        }

        JSONObject reviewedMeta = workspaceState == null ? null : workspaceState.optJSONObject("reviewedMeta");
        JSONObject pendingMeta = workspaceState == null ? null : workspaceState.optJSONObject("pendingReviewedMeta");
        JSONObject reviews = "pending".equals(module)
                ? (pendingMeta == null ? null : pendingMeta.optJSONObject(user))
                : (reviewedMeta == null ? null : reviewedMeta.optJSONObject(user));
        JSONObject historyMap = workspaceState == null ? null : workspaceState.optJSONObject("profileHistory");
        JSONObject history = historyMap == null ? null : historyMap.optJSONObject(user);

        if (reviews != null && reviews.optLong("reviewedAt", 0L) > 0L) {
            lines.add("Última revisión: " + dateTimeMillis(ctx, reviews.optLong("reviewedAt", 0L)));
            String decision = reviews.optString("decision", reviews.optString("reviewReason", ""));
            if (!decision.isBlank()) lines.add("Decisión: " + decision);
        } else if (!item.optString("reviewed_at", "").isBlank()) {
            lines.add("Última revisión: " + dateTime(ctx, item.optString("reviewed_at", "")));
            if (!item.optString("decision", "").isBlank())
                lines.add("Decisión: " + item.optString("decision"));
        } else {
            lines.add("Revisión: sin revisión confirmada en los datos disponibles");
        }

        if (history != null) {
            int opened = history.optInt("opened", 0);
            int reopened = history.optInt("reopened", 0);
            int reviewed = history.optInt("reviewed", 0);
            if (opened > 0 || reopened > 0 || reviewed > 0)
                lines.add("Historial: " + opened + " aperturas · " + reopened +
                        " reaperturas · " + reviewed + " revisiones");
            if (reviews == null && history.optLong("lastReviewed", 0L) > 0L)
                lines.add("Última revisión registrada: " +
                        dateTimeMillis(ctx, history.optLong("lastReviewed", 0L)));
        }
        if (row != null) {
            String riskLevel = row.optString("riskLevel", "");
            int riskScore = row.optInt("riskScore", -1);
            if (!riskLevel.isBlank())
                lines.add("Riesgo calculado: " + riskLevel +
                        (riskScore >= 0 ? " · " + riskScore + " puntos" : ""));
        }
        JSONObject provenance = "pending".equals(module) ? pendingRecord :
                followingRecord != null ? followingRecord : followerRecord;
        if (provenance != null && !provenance.optString("source", "").isBlank())
            lines.add("Origen en export: " + provenance.optString("source"));
        if (rawContext != null) {
            String historical = rawContext.optString("change", rawContext.optString("history", ""));
            if (!historical.isBlank()) lines.add("Cambio histórico: " + historical);
            String evidence = rawContext.optString("evidence", "");
            if (!evidence.isBlank()) lines.add("Evidencia: " + evidence);
            String reason = rawContext.optString("context", rawContext.optString("reason", ""));
            if (!reason.isBlank()) lines.add("Motivo de tanda: " + reason);
            if (rawContext.optBoolean("htmlUnknown", false)
                    || (row != null && row.optBoolean("htmlUnknown", false)))
                lines.add("AVISO: relación no verificable por export HTML parcial");
        }
        String status = item.optString("status", "pending");
        if ("opened".equals(status)) lines.add("Focus: abierto, pendiente de confirmar");
        else if ("reviewed".equals(status)) lines.add("Focus: revisión confirmada");
        return String.join("\n", lines);
    }

    static String batchHistory(Context ctx, JSONObject batch) {
        if (batch == null) return "Sin tandas registradas";
        String status = batch.optString("status", "");
        String state = switch (status) {
            case "completed" -> "Completada";
            case "active" -> "En curso";
            case "prepared" -> "Preparada";
            case "cancelled" -> "Cancelada";
            case "activity" -> "Actividad registrada";
            default -> status;
        };
        String label = batch.optString("label", "");
        int size = batch.optInt("target_size", 0);
        return "Última tanda: " + dateTime(ctx, batch.optString("created_at", "")) +
                (label.isBlank() ? "" : " · " + label) +
                (size > 0 ? " · " + size + " perfiles" : "") +
                " · " + state +
                " · " + batch.optString("created_device", "dispositivo desconocido") +
                ("completed".equals(status) ? "\nFinalizada: " +
                        dateTime(ctx, batch.optString("completed_at", "")) : "");
    }
}
