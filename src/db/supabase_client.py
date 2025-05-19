import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class SupabaseManager:
    def __init__(self):
        url = os.environ.get("SUPABASE_URL")
        key = os.environ.get("SUPABASE_KEY")
        self.supabase: Client = create_client(url, key)

    def insert_data(self, table_name, data):
        return self.supabase.table(table_name).insert(data).execute()

    def update_data(self, table_name, data, match_column, match_value):
        return self.supabase.table(table_name).update(data).eq(match_column, match_value).execute()

    def select_data(self, table_name, columns="*", filters=None):
        query = self.supabase.table(table_name).select(columns)
        if filters:
            for column, value in filters.items():
                query = query.eq(column, value)
        return query.execute()

    def delete_data(self, table_name, match_column, match_value):
        return self.supabase.table(table_name).delete().eq(match_column, match_value).execute() 