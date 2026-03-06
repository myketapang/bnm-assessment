#!/usr/bin/env python3
import pymysql
import argparse
from datetime import datetime
import sys
import glob
import re
import os
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "config.json")

with open(config_path, "r") as f:
    CONFIG = json.load(f)

# Load identity map
try:
    identity_files = glob.glob('identity_map_*.json')
    if identity_files:
        with open(max(identity_files), 'r') as f:
            IDENTITY_DATA = json.load(f)
        print(f"✓ Loaded identity map")
except:
    IDENTITY_DATA = {'identities': []}

class CompanyMigrator:
    # COMPREHENSIVE TABLE LIST - ALL MOODLE TABLES
    TABLES = [
        # CORE TABLES
        'mdl_user',
        'mdl_course_categories',
        'mdl_course',
        'mdl_course_modules',
        'mdl_cohort',
        'mdl_cohort_members',
        'mdl_enrol',
        'mdl_user_enrolments',
        'mdl_groups',
        'mdl_groups_members',
        'mdl_groupings',
        'mdl_groupings_groups',
        'mdl_course_completions',
        'mdl_course_completion_criteria',
        'mdl_course_completion_crit_compl',
        'mdl_course_modules_completion',
        'mdl_grade_items',
        'mdl_grade_grades',
        'mdl_grade_categories',
        'mdl_context',
        'mdl_role_assignments',
        'mdl_modules',
        
        # ATTENDANCE
        'mdl_attendance',
        'mdl_attendance_sessions',
        'mdl_attendance_log',
        'mdl_attendance_statuses',
        
        # QUIZ
        'mdl_quiz',
        'mdl_quiz_attempts',
        'mdl_quiz_grades',
        'mdl_quiz_slots',
        'mdl_quiz_feedback',
        'mdl_question',
        'mdl_question_attempts',
        'mdl_question_attempt_steps',
        'mdl_question_attempt_step_data',
        'mdl_question_categories',
        'mdl_question_references',
        'mdl_question_versions',
        'mdl_question_bank_entries',
        
        # ASSIGNMENT
        'mdl_assign',
        'mdl_assign_submission',
        'mdl_assign_grades',
        'mdl_assignsubmission_file',
        'mdl_assignsubmission_onlinetext',
        'mdl_assignsubmission_comments',
        'mdl_assign_plugin_config',
        'mdl_assign_user_flags',
        'mdl_assign_user_mapping',
        
        # FEEDBACK
        'mdl_feedback',
        'mdl_feedback_item',
        'mdl_feedback_value',
        'mdl_feedback_completed',
        'mdl_feedback_completedtmp',
        'mdl_feedback_valuetmp',
        
        # FILES / RESOURCES
        'mdl_files',
        'mdl_folder',
        'mdl_resource',
        'mdl_files_reference',
        'mdl_url',
        'mdl_page',
        'mdl_book',
        'mdl_book_chapters',
        
        # SCORM
        'mdl_scorm',
        'mdl_scorm_scoes',
        'mdl_scorm_scoes_data',
        'mdl_scorm_scoes_track',
        'mdl_scorm_aicc_session',
        
        # FORUM
        'mdl_forum',
        'mdl_forum_discussions',
        'mdl_forum_posts',
        'mdl_forum_subscriptions',
        'mdl_forum_read',
        'mdl_forum_track_prefs',
        
        # GOOGLE MEET
        'mdl_googlemeet',
        'mdl_googlemeet_events',
        'mdl_googlemeet_notify_done',
        
        # CERTIFICATE
        'mdl_certificate',
        'mdl_certificate_issues',
        'mdl_customcert',
        'mdl_customcert_elements',
        'mdl_customcert_issues',
        'mdl_customcert_pages',
        'mdl_customcert_templates',
        
        # BADGE
        'mdl_badge',
        'mdl_badge_issued',
        'mdl_badge_criteria',
        'mdl_badge_manual_award',
        'mdl_badge_backpack',
        
        # CHOICE
        'mdl_choice',
        'mdl_choice_answers',
        'mdl_choice_options',
        
        # LESSON
        'mdl_lesson',
        'mdl_lesson_pages',
        'mdl_lesson_answers',
        'mdl_lesson_attempts',
        'mdl_lesson_grades',
        
        # WORKSHOP
        'mdl_workshop',
        'mdl_workshop_submissions',
        'mdl_workshop_assessments',
        'mdl_workshop_grades',
        
        # WIKI
        'mdl_wiki',
        'mdl_wiki_pages',
        'mdl_wiki_versions',
        'mdl_wiki_subwikis',
        
        # GLOSSARY
        'mdl_glossary',
        'mdl_glossary_entries',
        'mdl_glossary_categories',
        
        # DATABASE ACTIVITY
        'mdl_data',
        'mdl_data_fields',
        'mdl_data_records',
        'mdl_data_content',
        
        # CHAT
        'mdl_chat',
        'mdl_chat_messages',
        'mdl_chat_users',
        
        # SURVEY
        'mdl_survey',
        'mdl_survey_analysis',
        'mdl_survey_answers',
        
        # H5P
        'mdl_h5p',
        'mdl_h5p_libraries',
        'mdl_h5pactivity',
        'mdl_h5pactivity_attempts',
        
        # LOGS
        'mdl_logstore_standard_log',
        'mdl_log',
        
        # ANALYTICS
        'mdl_analytics_predictions',
        'mdl_analytics_prediction_actions',
        
        # COMPETENCY
        'mdl_competency',
        'mdl_competency_framework',
        'mdl_competency_coursecomp',
        'mdl_competency_usercomp',
        
        # TAGS
        'mdl_tag',
        'mdl_tag_instance',
        
        # EVENTS
        'mdl_event',
        'mdl_event_subscriptions',
        
        # MESSAGES
        'mdl_message',
        'mdl_message_read',
        'mdl_message_contacts',
        'mdl_message_conversations',
        'mdl_message_conversation_members',
        
        # NOTIFICATIONS
        'mdl_notifications',
        
        # CALENDAR
        'mdl_calendar',
        'mdl_calendar_subscriptions',
        
        # BLOCKS
        'mdl_block_instances',
        'mdl_block_positions',
        
        # COMMENTS
        'mdl_comments',
        
        # RATINGS
        'mdl_rating',
        
        # NOTES
        'mdl_post',
    ]
    
    def __init__(self, company_code, dry_run=False):
        self.company_code = company_code
        self.dry_run = dry_run
        self.source_config = CONFIG['source_databases'][company_code]
        self.master_config = CONFIG['master_database']
        self.stats = {'tables': {}, 'total': 0, 'errors': [], 'skipped': []}
    
    def connect(self):
        print(f"\nConnecting...")
        self.source_conn = pymysql.connect(
            host=self.source_config['host'],
            port=self.source_config['port'],
            user=self.source_config['user'],
            password=self.source_config['password'],
            database=self.source_config['database'],
            connect_timeout=20
        )
        print(f"  ✓ Source: {self.source_config['database']}")
        
        self.master_conn = pymysql.connect(
            host=self.master_config['host'],
            port=self.master_config['port'],
            user=self.master_config['user'],
            password=self.master_config['password'],
            database=self.master_config['database'],
            connect_timeout=20
        )
        print(f"  ✓ Master: {self.master_config['database']}")
    
    def create_master_table(self, table):
        """Create master table WITHOUT PRIMARY KEY on id column"""
        master_table = f"master_{table}"
        
        cursor = self.master_conn.cursor()
        cursor.execute(f"SHOW TABLES LIKE '{master_table}'")
        if cursor.fetchone():
            return  # Table exists
        
        # Get source structure
        src_cursor = self.source_conn.cursor()
        src_cursor.execute(f"SHOW CREATE TABLE {table}")
        create_stmt = src_cursor.fetchone()[1]
        
        # Modify statement
        create_stmt = create_stmt.replace(f"CREATE TABLE `{table}`", f"CREATE TABLE `{master_table}`")
        
        # Remove AUTO_INCREMENT
        create_stmt = create_stmt.replace(' AUTO_INCREMENT', '')
        create_stmt = create_stmt.replace('AUTO_INCREMENT', '')
        
        # Remove PRIMARY KEY definition
        create_stmt = re.sub(r',?\s*PRIMARY KEY \(`[^`]+`\)', '', create_stmt)
        create_stmt = re.sub(r'PRIMARY KEY \(`[^`]+`\),?', '', create_stmt)
        
        # Add tracking columns at the beginning
        lines = create_stmt.split('\n')
        new_lines = [lines[0]]  # Keep CREATE TABLE
        
        # Add company_code
        new_lines.append("  `company_code` varchar(10) NOT NULL,")
        
        # Process remaining lines - rename id to legacy_id
        for line in lines[1:]:
            if '`id`' in line and 'INDEX' not in line and 'KEY' not in line:
                line = line.replace('`id`', '`legacy_id`')
            new_lines.append(line)
        
        create_stmt = '\n'.join(new_lines)
        
        # Add composite PRIMARY KEY before ENGINE
        create_stmt = create_stmt.replace(
            ') ENGINE=',
            ',\n  PRIMARY KEY (`company_code`, `legacy_id`),\n  KEY `idx_legacy_id` (`legacy_id`)\n) ENGINE='
        )
        
        # Clean up double commas
        create_stmt = create_stmt.replace(',,', ',')
        
        if not self.dry_run:
            try:
                cursor.execute(create_stmt)
                self.master_conn.commit()
            except Exception as e:
                # Table might exist or have issues - continue
                pass
    
    def migrate_table(self, table):
        try:
            src_cursor = self.source_conn.cursor()
            
            # Check if table exists in source
            src_cursor.execute(f"SHOW TABLES LIKE '{table}'")
            if not src_cursor.fetchone():
                self.stats['skipped'].append(f"{table} (not in source)")
                return 0
            
            # Get row count
            src_cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = src_cursor.fetchone()[0]
            
            if count == 0:
                self.stats['skipped'].append(f"{table} (empty)")
                return 0
            
            print(f"  📋 {table}: {count:,} rows", end='')
            
            if self.dry_run:
                print(" (would migrate)")
                return count
            
            # Create master table
            self.create_master_table(table)
            
            # Get columns
            src_cursor.execute(f"DESCRIBE {table}")
            columns = [row[0] for row in src_cursor.fetchall()]
            col_list = ', '.join([f"`{c}`" for c in columns])
            
            # Fetch data
            src_cursor.execute(f"SELECT {col_list} FROM {table}")
            
            # Insert into master
            master_table = f"master_{table}"
            master_cursor = self.master_conn.cursor()
            
            # Build INSERT with legacy_id
            insert_columns = ['company_code']
            for col in columns:
                if col == 'id':
                    insert_columns.append('legacy_id')
                else:
                    insert_columns.append(col)
            
            placeholders = ', '.join(['%s'] * (len(columns) + 1))
            insert_cols = ', '.join([f"`{c}`" for c in insert_columns])
            insert_sql = f"INSERT INTO {master_table} ({insert_cols}) VALUES ({placeholders})"
            
            inserted = 0
            batch = []
            
            for row in src_cursor:
                values = (self.company_code,) + row
                batch.append(values)
                
                if len(batch) >= 500:
                    master_cursor.executemany(insert_sql, batch)
                    self.master_conn.commit()
                    inserted += len(batch)
                    batch = []
                    print(f"\r  📋 {table}: {inserted:,}/{count:,}", end='')
            
            if batch:
                master_cursor.executemany(insert_sql, batch)
                self.master_conn.commit()
                inserted += len(batch)
            
            print(f"\r  ✓ {table}: {inserted:,} rows migrated")
            return inserted
            
        except Exception as e:
            print(f"\r  ✗ {table}: {e}")
            self.stats['errors'].append(f"{table}: {e}")
            return 0
    
    def migrate(self):
        print(f"\n{'='*80}")
        print(f"MIGRATING: {self.company_code} - {self.source_config['company_name']}")
        print(f"Mode: {'DRY RUN' if self.dry_run else 'PRODUCTION'}")
        print(f"Processing {len(self.TABLES)} tables")
        print(f"{'='*80}")
        
        self.connect()
        
        for table in self.TABLES:
            rows = self.migrate_table(table)
            self.stats['tables'][table] = rows
            self.stats['total'] += rows
        
        self.source_conn.close()
        self.master_conn.close()
        
        return self.stats
    
    def print_summary(self):
        print(f"\n{'='*80}")
        print(f"SUMMARY: {self.company_code}")
        print(f"{'='*80}")
        print(f"Total rows migrated: {self.stats['total']:,}")
        print(f"Tables processed: {len([t for t in self.stats['tables'].values() if t > 0])}")
        print(f"Tables skipped: {len(self.stats['skipped'])}")
        
        # Top tables by volume
        print(f"\nTop tables by volume:")
        sorted_tables = sorted(
            [(k, v) for k, v in self.stats['tables'].items() if v > 0],
            key=lambda x: x[1],
            reverse=True
        )
        
        for table, count in sorted_tables[:15]:
            print(f"  {table:40s}: {count:>10,}")
        
        if len(sorted_tables) > 15:
            print(f"  ... and {len(sorted_tables) - 15} more tables")
        
        if self.stats['errors']:
            print(f"\n⚠ Errors ({len(self.stats['errors'])}):")
            for e in self.stats['errors'][:10]:
                print(f"  - {e}")
            if len(self.stats['errors']) > 10:
                print(f"  ... and {len(self.stats['errors']) - 10} more errors")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('company_code')
    parser.add_argument('--dry-run', action='store_true')
    args = parser.parse_args()
    
    if args.company_code not in CONFIG['source_databases']:
        print(f"✗ Unknown company: {args.company_code}")
        return 1
    
    migrator = CompanyMigrator(args.company_code, args.dry_run)
    migrator.migrate()
    migrator.print_summary()
    
    if args.dry_run:
        print(f"\n✓ DRY RUN COMPLETE")
        print(f"Run: python3 migrate_company.py {args.company_code}")
    else:
        print(f"\n✓ MIGRATION COMPLETE")
        print(f"Next: python3 validate_migration.py {args.company_code}")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
