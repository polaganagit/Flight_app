import mysql.connector
from datetime import datetime

# ==================== DATABASE CONNECTION ====================
def connect_database():
    """Connect to MySQL database"""
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='root',
            password='your_actual_password',    # Change if you used different password
            database='flight_app'
        )
        print("✅ Database connected successfully!\n")
        return connection
    except mysql.connector.Error as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Troubleshooting:")
        print("1. Make sure MySQL is running")
        print("2. Check username and password")
        print("3. Make sure you created 'flight_app' database\n")
        return None


# ==================== ADD AIRPORT ====================
def add_airport(connection):
    """Add a new airport"""
    try:
        iata_code = input("Enter Airport IATA Code (e.g., DEL, BOM): ").strip().upper()
        
        cursor = connection.cursor()
        query = "INSERT INTO airports (iata_code) VALUES (%s)"
        cursor.execute(query, (iata_code,))
        connection.commit()
        
        print(f"\n✅ Airport {iata_code} added successfully!\n")
        cursor.close()
        
    except mysql.connector.IntegrityError:
        print(f"\n❌ Airport {iata_code} already exists!\n")
    except Exception as e:
        print(f"❌ Error: {e}")


# ==================== VIEW ALL AIRPORTS ====================
def view_airports(connection):
    """Display all airports"""
    try:
        cursor = connection.cursor()
        query = "SELECT * FROM airports ORDER BY iata_code"
        cursor.execute(query)
        
        airports = cursor.fetchall()
        
        if len(airports) == 0:
            print("\n❌ No airports found. Please add airports first.\n")
        else:
            print("\n" + "="*40)
            print("AVAILABLE AIRPORTS")
            print("="*40)
            print(f"{'ID':<10} {'IATA Code':<15}")
            print("-"*40)
            
            for airport in airports:
                print(f"{airport[0]:<10} {airport[1]:<15}")
            
            print("="*40 + "\n")
        
        cursor.close()
        return airports
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


# ==================== CREATE SEARCH ====================
def create_search(connection):
    """Create a new flight search"""
    try:
        airports = view_airports(connection)
        
        if len(airports) < 2:
            print("❌ Need at least 2 airports to search flights.\n")
            return None
        
        source_id = int(input("Enter Source Airport ID: "))
        destination_id = int(input("Enter Destination Airport ID: "))
        
        if source_id == destination_id:
            print("\n❌ Source and destination cannot be same!\n")
            return None
        
        travel_date = input("Enter Travel Date (YYYY-MM-DD): ").strip()
        
        try:
            datetime.strptime(travel_date, '%Y-%m-%d')
        except ValueError:
            print("\n❌ Invalid date format! Use YYYY-MM-DD\n")
            return None
        
        cursor = connection.cursor()
        query = """
            INSERT INTO searches (source_airport_id, destination_airport_id, travel_date)
            VALUES (%s, %s, %s)
        """
        cursor.execute(query, (source_id, destination_id, travel_date))
        connection.commit()
        
        search_id = cursor.lastrowid
        
        print(f"\n✅ Search created successfully! Search ID: {search_id}\n")
        cursor.close()
        
        return search_id
        
    except ValueError:
        print("\n❌ Please enter valid numbers!\n")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None


# ==================== VIEW ALL SEARCHES ====================
def view_searches(connection):
    """Display all searches"""
    try:
        cursor = connection.cursor()
        query = """
            SELECT 
                s.search_id,
                a1.iata_code AS source,
                a2.iata_code AS destination,
                s.travel_date,
                s.search_timestamp
            FROM searches s
            JOIN airports a1 ON s.source_airport_id = a1.airport_id
            JOIN airports a2 ON s.destination_airport_id = a2.airport_id
            ORDER BY s.search_id DESC
        """
        cursor.execute(query)
        
        searches = cursor.fetchall()
        
        if len(searches) == 0:
            print("\n❌ No searches found.\n")
        else:
            print("\n" + "="*80)
            print("ALL SEARCHES")
            print("="*80)
            print(f"{'ID':<8} {'From':<10} {'To':<10} {'Date':<15} {'Search Time':<20}")
            print("-"*80)
            
            for search in searches:
                print(f"{search[0]:<8} {search[1]:<10} {search[2]:<10} {search[3]:<15} {search[4]}")
            
            print("="*80 + "\n")
        
        cursor.close()
        return searches
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return []


# ==================== ADD FLIGHT ====================
def add_flight(connection):
    """Add a flight to a search"""
    try:
        searches = view_searches(connection)
        
        if len(searches) == 0:
            print("❌ Create a search first!\n")
            return
        
        search_id = int(input("Enter Search ID to add flight: "))
        
        print("\n--- Enter Flight Details ---")
        airline = input("Airline Name: ").strip()
        departure_airport = input("Departure Airport (IATA): ").strip().upper()
        arrival_airport = input("Arrival Airport (IATA): ").strip().upper()
        departure_time = input("Departure Time (YYYY-MM-DD HH:MM:SS): ").strip()
        arrival_time = input("Arrival Time (YYYY-MM-DD HH:MM:SS): ").strip()
        duration_minutes = int(input("Duration (minutes): "))
        price = float(input("Price: "))
        
        cursor = connection.cursor()
        query = """
            INSERT INTO flights 
            (search_id, airline, departure_airport, arrival_airport, 
             departure_time, arrival_time, duration_minutes, price)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (
            search_id, airline, departure_airport, arrival_airport,
            departure_time, arrival_time, duration_minutes, price
        ))
        connection.commit()
        
        print(f"\n✅ Flight added successfully!\n")
        cursor.close()
        
    except ValueError:
        print("\n❌ Please enter valid numbers!\n")
    except Exception as e:
        print(f"❌ Error: {e}")


# ==================== VIEW FLIGHTS BY SEARCH ====================
def view_flights_by_search(connection):
    """Display flights for a search"""
    try:
        searches = view_searches(connection)
        
        if len(searches) == 0:
            return
        
        search_id = int(input("Enter Search ID to view flights: "))
        
        cursor = connection.cursor()
        query = """
            SELECT 
                flight_id, airline, departure_airport, arrival_airport,
                departure_time, arrival_time, duration_minutes, price
            FROM flights
            WHERE search_id = %s
            ORDER BY price
        """
        cursor.execute(query, (search_id,))
        
        flights = cursor.fetchall()
        
        if len(flights) == 0:
            print(f"\n❌ No flights found for Search ID {search_id}\n")
        else:
            print("\n" + "="*100)
            print(f"FLIGHTS FOR SEARCH ID: {search_id}")
            print("="*100)
            print(f"{'ID':<6} {'Airline':<20} {'From':<8} {'To':<8} {'Departure':<20} {'Arrival':<20} {'Dur(min)':<10} {'Price':<10}")
            print("-"*100)
            
            for flight in flights:
                print(f"{flight[0]:<6} {flight[1]:<20} {flight[2]:<8} {flight[3]:<8} {str(flight[4]):<20} {str(flight[5]):<20} {flight[6]:<10} ₹{flight[7]:<10}")
            
            print("="*100 + "\n")
        
        cursor.close()
        
    except ValueError:
        print("\n❌ Please enter a valid number!\n")
    except Exception as e:
        print(f"❌ Error: {e}")


# ==================== VIEW ALL FLIGHTS ====================
def view_all_flights(connection):
    """Display all flights"""
    try:
        cursor = connection.cursor()
        query = """
            SELECT 
                f.flight_id, f.airline, f.departure_airport, f.arrival_airport,
                f.departure_time, f.arrival_time, f.duration_minutes, f.price, f.search_id
            FROM flights f
            ORDER BY f.search_id, f.price
        """
        cursor.execute(query)
        
        flights = cursor.fetchall()
        
        if len(flights) == 0:
            print("\n❌ No flights found.\n")
        else:
            print("\n" + "="*110)
            print("ALL FLIGHTS")
            print("="*110)
            print(f"{'ID':<6} {'SrchID':<8} {'Airline':<20} {'From':<8} {'To':<8} {'Departure':<20} {'Arrival':<20} {'Dur':<8} {'Price':<10}")
            print("-"*110)
            
            for flight in flights:
                print(f"{flight[0]:<6} {flight[8]:<8} {flight[1]:<20} {flight[2]:<8} {flight[3]:<8} {str(flight[4]):<20} {str(flight[5]):<20} {flight[6]:<8} ₹{flight[7]:<10}")
            
            print("="*110 + "\n")
        
        cursor.close()
        
    except Exception as e:
        print(f"❌ Error: {e}")


# ==================== DELETE SEARCH ====================
def delete_search(connection):
    """Delete a search"""
    try:
        searches = view_searches(connection)
        
        if len(searches) == 0:
            return
        
        search_id = int(input("Enter Search ID to delete: "))
        
        confirm = input(f"\n⚠️  Delete search {search_id} and all flights? (yes/no): ").strip().lower()
        
        if confirm != 'yes':
            print("Operation cancelled.\n")
            return
        
        cursor = connection.cursor()
        query = "DELETE FROM searches WHERE search_id = %s"
        cursor.execute(query, (search_id,))
        connection.commit()
        
        if cursor.rowcount > 0:
            print(f"\n✅ Search {search_id} deleted successfully!\n")
        else:
            print(f"\n❌ Search {search_id} not found!\n")
        
        cursor.close()
        
    except ValueError:
        print("\n❌ Please enter a valid number!\n")
    except Exception as e:
        print(f"❌ Error: {e}")


# ==================== MAIN MENU ====================
def main_menu():
    """Main menu"""
    
    connection = connect_database()
    
    if connection is None:
        return
    
    while True:
        print("\n" + "="*50)
        print("       ✈️  FLIGHT SEARCH APPLICATION")
        print("="*50)
        print("\n📍 AIRPORT MANAGEMENT")
        print("1. Add Airport")
        print("2. View All Airports")
        print("\n🔍 SEARCH MANAGEMENT")
        print("3. Create New Search")
        print("4. View All Searches")
        print("5. Delete Search")
        print("\n✈️  FLIGHT MANAGEMENT")
        print("6. Add Flight to Search")
        print("7. View Flights by Search ID")
        print("8. View All Flights")
        print("\n9. Exit")
        print("="*50)
        
        choice = input("\nEnter your choice (1-9): ").strip()
        
        if choice == '1':
            add_airport(connection)
        elif choice == '2':
            view_airports(connection)
        elif choice == '3':
            create_search(connection)
        elif choice == '4':
            view_searches(connection)
        elif choice == '5':
            delete_search(connection)
        elif choice == '6':
            add_flight(connection)
        elif choice == '7':
            view_flights_by_search(connection)
        elif choice == '8':
            view_all_flights(connection)
        elif choice == '9':
            print("\n✈️  Thank you for using Flight Search Application!")
            print("Goodbye! 👋\n")
            break
        else:
            print("\n❌ Invalid choice! Please enter 1-9.\n")
    
    connection.close()
    print("Database connection closed.")


# ==================== RUN PROGRAM ====================
if __name__ == "__main__":
    main_menu()