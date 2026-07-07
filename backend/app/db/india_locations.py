"""Predefined India location seed — all States/UTs plus major districts/cities.

Used as the FALLBACK location master data so the register + report location
fields cover the whole country out of the box. Imported official datasets
(LGD / Census / Pincode) are layered on top of this via official_locations.sync,
so real imported locations always take precedence and this fills the gaps.

Shape: { "State/UT name": ["District or City", ...] }. Each district gets a
default constituency of the same name so it is selectable and routable.
"""

INDIA_LOCATIONS = {
    "Andhra Pradesh": [
        "Visakhapatnam", "Vijayawada", "Guntur", "Tirupati", "Nellore",
        "Kurnool", "Rajahmundry", "Kadapa", "Anantapur", "Kakinada",
    ],
    "Arunachal Pradesh": ["Itanagar", "Naharlagun", "Pasighat"],
    "Assam": ["Guwahati", "Dibrugarh", "Silchar", "Jorhat", "Nagaon"],
    "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga"],
    "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg"],
    "Goa": ["Panaji", "Margao", "Vasco da Gama"],
    "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Gandhinagar"],
    "Haryana": ["Gurugram", "Faridabad", "Panipat", "Ambala", "Hisar", "Karnal"],
    "Himachal Pradesh": ["Shimla", "Dharamshala", "Mandi", "Solan"],
    "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro"],
    "Karnataka": [
        "Bengaluru", "Mysuru", "Hubballi", "Mangaluru", "Belagavi",
        "Kalaburagi", "Davanagere", "Shivamogga", "Tumakuru",
    ],
    "Kerala": [
        "Kochi", "Thiruvananthapuram", "Kozhikode", "Thrissur",
        "Kollam", "Kannur", "Alappuzha",
    ],
    "Madhya Pradesh": ["Bhopal", "Indore", "Gwalior", "Jabalpur", "Ujjain", "Sagar"],
    "Maharashtra": [
        "Mumbai", "Mumbai Suburban", "Pune", "Nagpur", "Nashik",
        "Thane", "Aurangabad", "Solapur", "Kolhapur", "Amravati",
    ],
    "Manipur": ["Imphal", "Thoubal"],
    "Meghalaya": ["Shillong", "Tura"],
    "Mizoram": ["Aizawl", "Lunglei"],
    "Nagaland": ["Kohima", "Dimapur"],
    "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Berhampur", "Sambalpur"],
    "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali"],
    "Rajasthan": ["Jaipur", "Jodhpur", "Udaipur", "Kota", "Ajmer", "Bikaner"],
    "Sikkim": ["Gangtok", "Namchi"],
    "Tamil Nadu": [
        "Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem",
        "Tirunelveli", "Erode", "Vellore", "Thoothukudi",
    ],
    "Telangana": [
        "Hyderabad", "Warangal", "Nizamabad", "Karimnagar",
        "Khammam", "Ramagundam", "Secunderabad",
    ],
    "Tripura": ["Agartala", "Udaipur"],
    "Uttar Pradesh": [
        "Lucknow", "Kanpur", "Varanasi", "Agra", "Prayagraj", "Ghaziabad",
        "Noida", "Meerut", "Bareilly", "Aligarh", "Gorakhpur",
    ],
    "Uttarakhand": ["Dehradun", "Haridwar", "Roorkee", "Haldwani", "Nainital"],
    "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri"],
    # Union Territories
    "Delhi": ["New Delhi", "North Delhi", "South Delhi", "East Delhi", "West Delhi"],
    "Jammu and Kashmir": ["Srinagar", "Jammu", "Anantnag", "Baramulla"],
    "Ladakh": ["Leh", "Kargil"],
    "Puducherry": ["Puducherry", "Karaikal"],
    "Chandigarh": ["Chandigarh"],
    "Andaman and Nicobar Islands": ["Port Blair"],
    "Dadra and Nagar Haveli and Daman and Diu": ["Silvassa", "Daman", "Diu"],
    "Lakshadweep": ["Kavaratti"],
}
