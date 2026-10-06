package com.michelslab.igcleaner;

import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;

import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;

import java.util.ArrayList;
import java.util.List;

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

    private final List<Row> rows = new ArrayList<>();
    private final Listener listener;

    public WorkspaceProfileAdapter(Listener listener) {
        this.listener = listener;
    }

    public void submit(List<Row> next) {
        rows.clear();
        rows.addAll(next);
        notifyDataSetChanged();
    }

    @NonNull
    @Override
    public Holder onCreateViewHolder(@NonNull ViewGroup parent, int viewType) {
        return new Holder(LayoutInflater.from(parent.getContext())
                .inflate(R.layout.item_workspace_profile, parent, false));
    }

    @Override
    public void onBindViewHolder(@NonNull Holder holder, int position) {
        Row row = rows.get(position);
        holder.username.setText("@" + row.username);
        holder.detail.setText(row.detail);
        holder.badge.setText(row.badge);
        holder.itemView.setOnClickListener(v -> listener.onProfileClick(row));
    }

    @Override public int getItemCount() { return rows.size(); }

    static final class Holder extends RecyclerView.ViewHolder {
        final TextView username;
        final TextView detail;
        final TextView badge;

        Holder(@NonNull View itemView) {
            super(itemView);
            username = itemView.findViewById(R.id.workspaceUsername);
            detail = itemView.findViewById(R.id.workspaceDetail);
            badge = itemView.findViewById(R.id.workspaceBadge);
        }
    }
}
