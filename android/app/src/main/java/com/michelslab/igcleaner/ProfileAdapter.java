package com.michelslab.igcleaner;

import android.graphics.Typeface;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import com.google.android.material.checkbox.MaterialCheckBox;

import java.util.ArrayList;
import java.util.List;

public final class ProfileAdapter extends RecyclerView.Adapter<ProfileAdapter.Holder> {
    public interface Listener { void onProfileClick(ProfileRow row); }

    public static final class ProfileRow {
        public final String username;
        public final String detail;
        public boolean checked;
        public final String badge;
        public final Object payload;

        public ProfileRow(String username, String detail, boolean checked, String badge, Object payload) {
            this.username = username;
            this.detail = detail;
            this.checked = checked;
            this.badge = badge;
            this.payload = payload;
        }
    }

    private final List<ProfileRow> rows = new ArrayList<>();
    private final Listener listener;

    public ProfileAdapter(Listener listener) { this.listener = listener; }

    public void submit(List<ProfileRow> next) {
        rows.clear();
        rows.addAll(next);
        notifyDataSetChanged();
    }

    public List<ProfileRow> rows() { return rows; }

    @NonNull
    @Override
    public Holder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        View view = LayoutInflater.from(parent.getContext()).inflate(R.layout.item_profile, parent, false);
        return new Holder(view);
    }

    @Override
    public void onBindViewHolder(@NonNull Holder h, int position) {
        ProfileRow row = rows.get(position);
        h.check.setChecked(row.checked);
        h.username.setText("@" + row.username);
        h.username.setTypeface(null, Typeface.BOLD);
        h.detail.setText(row.detail == null || row.detail.isBlank() ? "Toca para abrir en Instagram" : row.detail);
        h.badge.setText(row.badge == null || row.badge.isBlank() ? (row.checked ? "ABIERTO" : "PENDIENTE") : row.badge);
        h.itemView.setOnClickListener(v -> listener.onProfileClick(row));
        h.check.setOnClickListener(v -> {
            h.check.setChecked(row.checked);
            listener.onProfileClick(row);
        });
    }

    @Override public int getItemCount() { return rows.size(); }

    static final class Holder extends RecyclerView.ViewHolder {
        final MaterialCheckBox check;
        final TextView username;
        final TextView detail;
        final TextView badge;

        Holder(@NonNull View itemView) {
            super(itemView);
            check = itemView.findViewById(R.id.profileCheck);
            username = itemView.findViewById(R.id.profileUsername);
            detail = itemView.findViewById(R.id.profileDetail);
            badge = itemView.findViewById(R.id.profileBadge);
        }
    }
}
