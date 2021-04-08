import os
import psycopg2
import psycopg2.extras

DATABASE_URL = os.environ['DATABASE_URL']

conn = psycopg2.connect(DATABASE_URL, sslmode='require')

# Retorna os summoners da tabela
def Summoner_Info():
    cur = conn.cursor()
    cur.execute("""Select * from summoners""")
    return cur.fetchall()
    
# Criar tabelas / Obter conteudo
def create_table():
    cur = conn.cursor()
    cur.execute("select exists(select * from information_schema.tables where table_name=%s)", ('summoners',))
    table_exists = cur.fetchone()[0]
    cur.close()

    if (not table_exists):
        try:
            cur = conn.cursor()
            cur.execute("""
            CREATE TABLE summoners (
                summoner_name text,
                lastmatch_id BIGINT NOT NULL,
                discord_id BIGINT NOT NULL,
                server_id BIGINT,
                ranks text,
                tier text,
                accountId text,
                id text
            )
            """)
            cur.close()
            conn.commit()
        except psycopg2.DatabaseError as error:
            print(error)
    else:
        try:
            cur = conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
            cur.execute ("""select summoner_name, lastmatch_id, discord_id, server_id, ranks, tier, accountId, id from summoners""")
            #ans = cur.fetchall()
            #for row in ans:
                #summoners[row[0]] = row[1]
            cur.close()
        except psycopg2.DatabaseError as error:
            print(error) 

def check_exists(curr_SumName, Db_SumName, curr_SvID, Db_SvID, Db_accID, Db_SumID, cur):
    if curr_SumName == Db_SumName and int(curr_SvID) == Db_SvID:
        if Db_accID == "0" or Db_SumID == "0":
            import UserFunc
            User = UserFunc.load_user_for_db(curr_SumName)
            cur.execute("UPDATE summoners SET accountId = %s, id = %s WHERE summoner_name = %s", (User["accountId"], User["id"], curr_SumName))
            conn.commit()
        return False
    return True

def importes(summoner_name):
    import UserFunc
    return UserFunc.load_user_for_db(summoner_name)

# Inserir colunas na tabela
def Insert_Into_Database(summoner_name, matchid, discord_id, server_id):
    try:
        cur = conn.cursor()
        cur.execute("""Select * from summoners""")
        ans = cur.fetchall()
        for row in ans:
            if(not check_exists(summoner_name,row[0],server_id,row[3],row[6],row[7],cur)):
                cur.close()
                return False
        User = importes(summoner_name)   
        cur.execute(""" INSERT INTO summoners (summoner_name, lastmatch_id, discord_id, server_id, accountId, id) VALUES (%s, %s, %s, %s,%s,%s); """, (summoner_name, matchid, discord_id, server_id,User["accountId"], User["id"]))
        print("'" + summoner_name + "'", "Was added to the database")
        cur.close()
        conn.commit()
        return True
    except  psycopg2.DatabaseError as error:
        print(error)
        
def get_user(Summoner_Name):
    try:
        cur = conn.cursor()
        cur.execute("Select accountId, id from summoners WHERE summoner_name = %s", (Summoner_Name,))
        ans = cur.fetchall()
        cur.close()
        if len(ans) == 0:
            print("That user does not exist!")
            return False
        conn.commit()
        dict = {
            "accountId": ans[0][0],
            "id": ans[0][1]
        }
        return dict
    except  psycopg2.DatabaseError as error:
        print(error)


# Atualizar colunas da tabela
def Update_database_lastmatch(summoner_name, lastmatch_id):
    try:
        cur = conn.cursor()
        cur.execute("UPDATE summoners SET lastmatch_id = %s WHERE summoner_name = %s",(lastmatch_id, summoner_name))
        cur.close()
        conn.commit()
    except psycopg2.DatabaseError as error:
        print(error)

def Update_database_rank(summoner_name,rank,tier):
    try:
        cur = conn.cursor()
        cur.execute("SELECT ranks, tier FROM summoners WHERE summoner_name = %s", (summoner_name,))
        ans = cur.fetchall()
        if ans[0][0] == rank and ans[0][1] == tier:
            #print("RANK_NEW: ",rank," TIER_NEW ", tier, " RANK_OLD: ", ans[0][0], " TIER_OLD: ", ans[0][1], " ON DB")
            return False
        print("Summoner:",summoner_name, "Went from ",ans[0][0],ans[0][1], "to ", rank,tier)
        cur.execute("UPDATE summoners SET ranks = %s, tier = %s WHERE summoner_name = %s",(rank, tier, summoner_name))
        cur.close()
        conn.commit()
        return ans[0][0],ans[0][1]
    except psycopg2.DatabaseError as error:
        print(error)

# Remover colunas da tabela
def Remove_From_Database(summoner_name):
    try:
        cur = conn.cursor()
        cur.execute("DELETE FROM summoners WHERE summoner_name = %s RETURNING *", (summoner_name,))
        ans = cur.fetchall()
        print(ans)
        conn.commit()
        cur.close()
        print(len(ans))
        if (len(ans) != 0):
            return True
        else:
            return False
    except psycopg2.DatabaseError as error:
        print(error)
