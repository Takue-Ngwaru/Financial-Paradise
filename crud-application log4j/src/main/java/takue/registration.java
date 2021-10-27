package takue;
import java.util.logging.Logger;
import java.sql.*;

import java.util.*;

public class registration {
	String url = "jdbc:mysql://localhost:3306/account-registration";
	String userName = "root";
	String psw = "takue1234";
	String query;
	final static Logger logger = Logger.getLogger(String.valueOf(registration.class));
public static void main(String[] args) {
		registration user = new registration();
		Scanner input = new Scanner(System.in);

		logger.info("Select Option");
		logger.info("1-----to create  \n" + "2-----to read  \n" + "3-----to update  \n" + "4-----to delete  \n");
		try {
			int userInput = input.nextInt();

			if (userInput == 1) {

				try {
					user.create();
				} catch (Exception e) {
					logger.severe("Got exception!");
}

			} else if (userInput == 2) {

				try {
					user.read();
				} catch (Exception e) {
					logger.severe("Got exception!");


					
				}

			}

			else if (userInput == 3) {

				try {
					user.update();
				} catch (Exception e) {
					logger.severe("Got exception!");



					
				}

			} else if (userInput == 4) {

				try {
					user.delete();
				} catch (Exception e) {
					logger.severe("Got exception!");



					
				}

			} else {
				logger.info("input is incorrect");

			}

		} catch (Exception e) {
			logger.severe("Got exception!");


			
		}

	}

	public void create() {
		String email;
		String firstname;
		String surname;
		String dateOfBirth;
		String Phonenumber;
		String address;
		Scanner input = new Scanner(System.in);
		logger.info("enter email: ");
		email = input.nextLine();
		logger.info(" ");
		logger.info("enter firstname: ");
		firstname = input.nextLine();
		logger.info(" ");
		logger.info("enter surname: ");
		surname = input.nextLine();
		logger.info("enter date of birth: ");
		dateOfBirth = input.nextLine();
		logger.info("enter phone number: ");
		Phonenumber = input.nextLine();
		logger.info("enter address: ");
		address = input.nextLine();
		logger.info(" ");

		try {

			Class.forName("com.mysql.cj.jdbc.Driver");
			Connection con = DriverManager.getConnection(url, userName, psw);
			query = "INSERT INTO login_page (email,firstname,surname,dateOfBirth,Phonenumber,address )"
					+ "VALUES(?,?,?,?,?,?)";

			PreparedStatement Stmt = con.prepareStatement(query);

			Stmt.setString(1, email);
			Stmt.setString(2, firstname);
			Stmt.setString(3, surname);
			Stmt.setString(4, dateOfBirth);
			Stmt.setString(5, Phonenumber);
			Stmt.setString(6, address);

			Stmt.execute();
			logger.info("data inserted successfully");
			logger.info("Select Option");
			logger.info(
					"1-----to create  \n" + "2-----to read  \n" + "3-----to update  \n" + "4-----to delete  \n");

			con.close();

		} catch (Exception e) {
			logger.severe("Got exception!");


			
		}

	}

	public void read() {
		try {
			Class.forName("com.mysql.cj.jdbc.Driver");
			Connection con = DriverManager.getConnection(url, userName, psw);
			Statement st = con.createStatement();
			query = "SELECT * FROM login_page";
			st.executeQuery(query);
			ResultSet rs = st.executeQuery(query);
			while (rs.next()) {
				logger.info(rs.getString(1) + "  " + rs.getString(2) + " " + rs.getString(3) + "  "
						+ rs.getString(4) + " " + rs.getString(5) + " " + rs.getString(6));
			}

		} catch (Exception e) {
			logger.severe("Got exception!");


			
		}
	}

	public void update() {
		String email;
		String Phonenumber;
		Scanner input = new Scanner(System.in);
		logger.info("enter email: ");
		email = input.nextLine();
		logger.info("enter Phonenumber: ");
		Phonenumber = input.nextLine();

		try {
			Class.forName("com.mysql.cj.jdbc.Driver");
			Connection con = DriverManager.getConnection(url, userName, psw);
			Statement st = con.createStatement();
			String query = "UPDATE login_page SET Phonenumber =? WHERE email=?";
			PreparedStatement statement = con.prepareStatement(query);
			statement.setString(1, Phonenumber);
			statement.setString(2, email);
			statement.execute();
			logger.info("data updated");

			con.close();

		} catch (Exception e) {
			logger.severe("Got exception!");


			
		}

	}

	public void delete() {

		try {
			Scanner input = new Scanner(System.in);
			logger.info("enter firstname: ");
			String name = input.nextLine();

			Class.forName("com.mysql.cj.jdbc.Driver");
			Connection con = DriverManager.getConnection(url, userName, psw);
			query = "DELETE FROM login_page WHERE firstname = ?";
			PreparedStatement preparedStmt = con.prepareStatement(query);
			preparedStmt.setString(1, name);
			preparedStmt.execute();
			logger.info("the row has being delected");
			con.close();

		} catch (Exception e) {
			logger.severe("Got exception!");
;
			
			

			
		}

	}
}
