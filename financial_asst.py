import openai
import streamlit as st
import pandas as pd
import plotly as px
import os

# Set your OpenAI API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# File path to save the expenses data
EXPENSES_FILE = "expenses_data.csv"

# Load expenses data from CSV file
def load_expenses():
    if os.path.exists(EXPENSES_FILE):
        return pd.read_csv(EXPENSES_FILE)
    return pd.DataFrame(columns=["date", "description", "amount", "category"])

# Save expenses data to CSV file
def save_expenses(expenses_df):
    expenses_df.to_csv(EXPENSES_FILE, index=False)

# Initialize session state for storing expenses
if "expenses" not in st.session_state:
    st.session_state.expenses = load_expenses()

st.markdown("""
    <h1 style='color: #f9f95d; font-size: 60px;'>
        <i class="fas fa-wallet"></i> Financial Assistance
    </h1>
""", unsafe_allow_html=True)


# Function to interact with OpenAI API for saving suggestions
def get_saving_tips(income, goal, time_frame, previous_expenses_df):
    previous_expenses_summary = previous_expenses_df.groupby('category')['amount'].sum().to_dict()
    messages = [
        {"role": "system", "content": "You are an insightful financial assistant."},
        {"role": "user", "content": f"I have a monthly income of RM{income}, and I want to save RM{goal} in {time_frame} months. Based on my {previous_expenses_summary} spending, suggest ways to save."}
    ]
    with st.spinner("Generating saving strategies..."):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000
        )

    
    suggestions = response.choices[0].message.content.strip()
    return suggestions

# Function to categorize expenses using OpenAI
# Function to categorize expenses using OpenAI
def categorize_expenses(expense_description):
    allowed_categories = [
        "housing", "transportation", "food", "utilities", "insurance", 
        "healthcare", "saving", "investment", "debt payment", 
        "personal spending", "entertainment", "miscellaneous"
    ]
    
    messages = [
        {"role": "system", "content": "You are an assistant that helps categorize expenses."},
        {"role": "user", "content": f"""The expense is: {expense_description}. Can you categorize this expense? 
        The categories should only be one of the following: {", ".join(allowed_categories)}."""}
    ]
    
    with st.spinner("Categorizing expense..."):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=300
        )

    
    # Extract the response and clean it
    category_response = response.choices[0].message.content.strip().lower()

    # Check if the response contains a valid category
    for category in allowed_categories:
        if category in category_response:
            return category.capitalize()  # Capitalize the first letter for consistency

    return "Miscellaneous"  # Default category if no match is found


# Function to generate a budget based on the previous month’s expenses
def generate_budget(income, previous_expenses_df):
    # Summarize previous month’s spending by category
    previous_expenses_summary = previous_expenses_df.groupby('category')['amount'].sum().to_dict()
    
    # Prepare message for GPT analysis
    messages = [
        {"role": "system", "content": "You are a financial assistant that helps users create budgets based on their income and previous expenses."},
        {"role": "user", "content": f"My monthly income is RM{income}. Here are my previous expenses by category: {previous_expenses_summary}. Can you suggest a budget allocation including essentials (food, rent), savings, and discretionary spending?"}
    ]
    
    with st.spinner("Generating budget..."):
        response = openai.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            max_tokens=1000
        )

    
    budget = response.choices[0].message.content.strip()
    
    return budget

# Create a selectbox for page navigation
page = st.sidebar.selectbox("Choose a feature", ["Budgeting", "Expense Tracker", "Financial Goals"])

# Budgeting Page
if page == "Budgeting":
    st.title("Budgeting")
    
    # Input for income and viewing budget by month
    income = st.number_input("Enter your monthly income (RM):", min_value=0, step=100)
    selected_month = st.sidebar.selectbox("Select Month", pd.to_datetime(st.session_state.expenses['date']).dt.strftime('%Y-%m').unique())

    # Filter previous expenses by selected month
    if selected_month:
        previous_expenses = st.session_state.expenses[pd.to_datetime(st.session_state.expenses['date']).dt.strftime('%Y-%m') == selected_month]
    
    if st.button("Generate Budget"):
        if income > 0 and not previous_expenses.empty:
            budget = generate_budget(income, previous_expenses)
            
            st.write("Here is your suggested budget:")
            # Budget breakdown for visualization
            budget_df = pd.DataFrame({
                "Category": ["Essentials", "Savings", "Discretionary Spending"],
                "Amount (RM)": [1950, 1100, 2450]
            })

            # Pie chart to show how income is divided
            fig_budget = px.pie(budget_df, values="Amount (RM)", names="Category", title="Suggested Budget Allocation", hole=0.4)
            st.plotly_chart(fig_budget)

            st.write(budget)
        else:
            st.warning("Please enter your income and ensure there are expenses for the selected month.")

# Expense Tracker Page
elif page == "Expense Tracker":
    st.title("Expense Tracker")
    
    # Input for expense details
    income = st.sidebar.number_input("Enter your monthly income (RM):", min_value=0, step=100)
    selected_month = st.sidebar.selectbox("Select Month to View", pd.to_datetime(st.session_state.expenses['date']).dt.strftime('%Y-%m').unique())
    expense_date = st.sidebar.date_input("Date of Expense")
    expense_description = st.sidebar.text_input("Enter a brief description of the expense:")
    expense_amount = st.sidebar.number_input("Enter the expense amount (RM):", min_value=0, step=10)
    
    # Handle categorization and expense input
    if st.sidebar.button("Categorize and Add Expense"):
        if expense_description and expense_amount > 0:
            category = categorize_expenses(expense_description)
            new_expense = {
                "date": expense_date,
                "description": expense_description,
                "amount": expense_amount,
                "category": category
            }
            new_expense_df = pd.DataFrame([new_expense])
            st.session_state.expenses = pd.concat([st.session_state.expenses, new_expense_df], ignore_index=True)
            save_expenses(st.session_state.expenses)
            st.sidebar.success(f"Expense categorized as {category} and added!")
        else:
            st.sidebar.warning("Please enter both expense description and amount.")

    # Display expenses by selected month
    
    if selected_month:
        month_expenses = st.session_state.expenses[pd.to_datetime(st.session_state.expenses['date']).dt.strftime('%Y-%m') == selected_month]
        st.write(f"Expenses for {selected_month}:")
        st.dataframe(month_expenses)

        # Create a pie chart of expenses by category using Plotly
        category_totals = month_expenses.groupby("category")["amount"].sum().reset_index()
        fig = px.pie(category_totals, values="amount", names="category", title="Expenses by Category")
        st.plotly_chart(fig)

        # Check if spending exceeds income for the selected month
        total_expenses = st.session_state.expenses["amount"].sum()
        if income > 0:
            if total_expenses > income:
                st.warning(f"Your total expenses (RM{total_expenses}) have exceeded your income (RM{income})!")
            else:
                st.success(f"Your total expenses (RM{total_expenses}) are within your income (RM{income}).")

# Financial Goals Page
elif page == "Financial Goals":
    st.title("Financial Goals")

    # Input for savings goal and time frame
    income = st.number_input("Enter your monthly income (RM):", min_value=0, step=100)
    goal_amount = st.number_input("Enter your savings goal (RM):", min_value=0, step=100)
    time_frame = st.number_input("Enter your time frame (in months):", min_value=1, step=1)
    tips=""
    
    if st.button("Get Saving Strategies"):
        if income > 0 and goal_amount > 0 and time_frame > 0:
            tips = get_saving_tips(income, goal_amount, time_frame, st.session_state.expenses)
            st.write("Here are some saving strategies for your goal:")
        else:
            st.warning("Please enter valid values for income, goal, and time frame.")

    # Create tabs for visualization and tips
    tab1, tab2 = st.tabs(["Savings Strategies", "Visualizations"])

    with tab1:
        # Display saving strategies tips
        st.write(tips)

    with tab2:
        # Data visualization for savings goal
        if income > 0:
            monthly_savings = goal_amount / time_frame
            budget_for_savings = income - monthly_savings

            # Create a DataFrame for visualization
            savings_data = pd.DataFrame({
                "Category": ["Monthly Income", "Savings Goal", "Remaining Budget"],
                "Amount (RM)": [income, monthly_savings, budget_for_savings]
            })

            # Bar chart to visualize savings goal and budget
            fig = px.bar(savings_data, x="Category", y="Amount (RM)", title="Savings Goal Visualization", text="Amount (RM)")
            st.plotly_chart(fig)

            # Optional: Pie chart for budget allocation if relevant
            budget_df = pd.DataFrame({
                "Category": ["Savings", "Remaining Budget"],
                "Amount (RM)": [monthly_savings, budget_for_savings]
            })
            fig_budget = px.pie(budget_df, values="Amount (RM)", names="Category", title="Budget Allocation", hole=0.4)
            st.plotly_chart(fig_budget)

