package com.michelslab.igcleaner;

import static org.junit.Assert.assertEquals;
import static org.junit.Assert.assertThrows;

import org.junit.Test;

/** Verified on actual installed debug APK, compact and wide emulator viewports. */
public class InstagramAccountScopeTest {
    @Test public void legacyUsesUnmodifiedPreviouslyPublishedEndpoints() {
        assertEquals("list_snapshots?select=*", SyncApi.scopeQuery("list_snapshots?select=*", "legacy"));
        assertEquals("focus_batches?select=*&limit=30", SyncApi.scopeQuery("focus_batches?select=*&limit=30", "legacy"));
    }

    @Test public void everyInstagramProfileHasIndependentRemoteListAndBatchPaths() {
        assertEquals("instagram_list_snapshots?select=payload&account_key=eq.ig_one_123",
                SyncApi.scopeQuery("list_snapshots?select=payload", "ig_one_123"));
        assertEquals("instagram_list_snapshots?select=payload&account_key=eq.ig_two_456",
                SyncApi.scopeQuery("list_snapshots?select=payload", "ig_two_456"));
        assertEquals("instagram_focus_batches?id=eq.batch&account_key=eq.ig_two_456",
                SyncApi.scopeQuery("focus_batches?id=eq.batch", "ig_two_456"));
        assertEquals("instagram_workspace_state?state_key=eq.primary&account_key=eq.ig_one_123",
                SyncApi.scopeQuery("workspace_state?state_key=eq.primary", "ig_one_123"));
    }

    @Test public void authAccountRegistryAndOtherUsersAreNotFakedAsScopedProfileTables() {
        assertEquals("instagram_accounts?select=*", SyncApi.scopeQuery("instagram_accounts?select=*", "ig_one_123"));
        assertEquals("devices?select=*", SyncApi.scopeQuery("devices?select=*", "ig_one_123"));
        assertThrows(IllegalArgumentException.class,
                () -> SyncApi.scopeQuery("list_snapshots?select=*", "attacker%26user_id%3Deq.other"));
    }
}
