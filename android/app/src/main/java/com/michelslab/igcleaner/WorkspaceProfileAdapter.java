package com.michelslab.igcleaner;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;
import java.util.List;
import java.util.Locale;

public final class WorkspaceProfileAdapter extends RecyclerView.Adapter<WorkspaceProfileAdapter.Holder> {
    public interface Listener { void onProfileClick(Row row); }

    public static final class Row {
        public final String username;
        public final String detail;
        public final String badge;

        public Row(String username, String detail, String badge) {
            this.username = username;
            this.detail = detail;
            this.badge = badge;
        }
    }

    private final List<Row> allRows = new ArrayList<>();
    private final List<Row> rows = new ArrayList<>();
    private final Listener listener;

    public WorkspaceProfileAdapter(Listener listener) { this.listener = listener; }

    public void submit(List<Row> next) {
        allRows.clear();
        allRows.addAll(next);
        rows.clear();
        rows.addAll(next);
        notifyDataSetChanged();
    }

    public void filter(String query) {
        String q = query == null ? "" : query.trim().toLowerCase(Locale.ROOT);
        rows.clear();
        if (q.isBlank()) rows.addAll(allRows);
        else for (Row row : allRows) if (row.username.toLowerCase(Locale.ROOT).contains(q)) rows.add(row);
        notifyDataSetChanged();
    }

    @NonNull
    @Override public Holder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        return new Holder(LayoutInflater.from(parent.getContext()).inflate(R.layout.item_workspace_profile, parent, false));
    }

    @Override public void onBindViewHolder(@NonNull Holder h, int position) {
        Row row = rows.get(position);
        h.avatar.setText(row.username.isBlank() ? "@" : row.username.substring(0,1).toUpperCase(Locale.ROOT));
        h.username.setText("@" + row.username);
        h.detail.setText(row.detail);
        h.badge.setText(row.badge);
        h.itemView.setOnClickListener(v -> listener.onProfileClick(row));
    }

    @Override public int getItemCount() { return rows.size(); }

    static final class Holder extends RecyclerView.ViewHolder {
        final TextView avatar, username, detail, badge;
        Holder(@NonNull View itemView) {
            super(itemView);
            avatar = itemView.findViewById(R.id.workspaceAvatar);
            username = itemView.findViewById(R.id.workspaceUsername);
            detail = itemView.findViewById(R.id.workspaceDetail);
            badge = itemView.findViewById(R.id.workspaceBadge);
        }
    }
}