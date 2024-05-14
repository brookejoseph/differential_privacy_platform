import streamlit as st
import numpy as np
import pandas as pd

class LaplaceMechanism:
    def __init__(self, epsilon):
        self.epsilon = epsilon

    def add_noise(self, true_count):
        noisy_count = true_count + np.random.laplace(scale=1/self.epsilon)
        return noisy_count

def main():
    st.title("Differentially Private Database")

    # Create instance of LaplaceMechanism
    epsilon = st.sidebar.number_input("Epsilon", value=0.5, step=0.1)
    laplace_mechanism = LaplaceMechanism(epsilon)

    # Sidebar for user inputs
    st.sidebar.header("Actions")
    action = st.sidebar.selectbox("Select Action", ("Upload Dataset", "View Private Data", "Query"))

    if action == "Upload Dataset":
        st.sidebar.subheader("Upload CSV Dataset")
        uploaded_file = st.sidebar.file_uploader("Choose a CSV file", type="csv")
        if uploaded_file is not None:
            df = pd.read_csv(uploaded_file)
            st.write("### Raw Dataset")
            st.write(df)

            # Store the dataset in memory
            st.session_state.raw_dataset = df

            st.success("Dataset Uploaded Successfully!")

    elif action == "View Private Data":
        if "raw_dataset" not in st.session_state:
            st.warning("Please upload a dataset first.")
            return

        st.write("### Private Dataset")

        if "raw_dataset" in st.session_state:
            private_dataset = st.session_state.raw_dataset.copy()
            for column in private_dataset.columns:
                if column != "unnamed":
                    private_dataset[column] = laplace_mechanism.add_noise(private_dataset[column])
            st.write(private_dataset)
        else:
            st.warning("No private dataset available. Please upload a dataset and perform a query.")

    elif action == "Query":
        if "raw_dataset" not in st.session_state:
            st.warning("Please upload a dataset first.")
            return

        st.write("### Raw Dataset")
        st.write(st.session_state.raw_dataset)

        st.sidebar.subheader("SQL-Like Queries")
        query_function = st.sidebar.selectbox("Select Query Function", ("Insert", "Delete"))

        if query_function == "Insert":
            st.sidebar.subheader("Insert Record")
            column_names = st.session_state.raw_dataset.columns.tolist()
            insert_values = {}
            for column in column_names:
                if column != "unnamed":
                    insert_values[column] = st.sidebar.text_input(f"Enter value for {column}")

            if st.sidebar.button("Insert"):
                new_record = pd.DataFrame([insert_values])
                st.session_state.raw_dataset = pd.concat([st.session_state.raw_dataset, new_record], ignore_index=True)
                st.success("Record Inserted Successfully!")

        elif query_function == "Delete":
            st.sidebar.subheader("Delete Record")
            condition_column = st.sidebar.selectbox("Condition Column", st.session_state.raw_dataset.columns.tolist())
            condition_value = st.sidebar.text_input("Condition Value")

            if st.sidebar.button("Delete"):
                st.session_state.raw_dataset = st.session_state.raw_dataset[st.session_state.raw_dataset[condition_column] != condition_value]
                st.success("Record(s) Deleted Successfully!")

if __name__ == "__main__":
    main()
