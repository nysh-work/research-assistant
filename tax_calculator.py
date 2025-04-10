import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime

# --- Tax Calculator Tool ---
# This tool helps chartered accountants with tax calculations and financial analysis

def tax_calculator_tab():
    """Render the tax calculator tab in the Streamlit app."""
    st.header("💰 Tax Calculator")
    st.info("Calculate income tax liability, compare tax scenarios, and analyze deductions for financial planning.", icon="💡")
    
    # Create tabs for different tax calculation features
    calc_tabs = st.tabs(["Income Tax Calculator", "Tax Comparison", "Deduction Analyzer"])
    
    # Tab 1: Income Tax Calculator
    with calc_tabs[0]:
        st.subheader("Income Tax Calculator")
        
        # Select assessment year
        assessment_year = st.selectbox(
            "Assessment Year",
            options=[f"{year}-{year+1}" for year in range(2023, 2020, -1)],
            index=0,
            help="Select the assessment year for tax calculation."
        )
        
        # Select tax regime
        tax_regime = st.radio(
            "Tax Regime",
            options=["Old Regime", "New Regime"],
            index=0,
            horizontal=True,
            help="Select the applicable tax regime."
        )
        
        # Income details
        with st.container(border=True):
            st.markdown("**Income Details**")
            
            col1, col2 = st.columns(2)
            with col1:
                salary_income = st.number_input("Salary Income", min_value=0, value=0, step=10000)
                business_income = st.number_input("Business Income", min_value=0, value=0, step=10000)
                capital_gains = st.number_input("Capital Gains", min_value=0, value=0, step=10000)
            
            with col2:
                house_property_income = st.number_input("Income from House Property", min_value=-200000, value=0, step=10000)
                other_income = st.number_input("Other Income", min_value=0, value=0, step=10000)
        
        # Deductions (only for old regime)
        if tax_regime == "Old Regime":
            with st.container(border=True):
                st.markdown("**Deductions**")
                
                col1, col2 = st.columns(2)
                with col1:
                    sec_80c = st.number_input("Section 80C (max ₹1,50,000)", min_value=0, max_value=150000, value=0, step=5000)
                    sec_80d = st.number_input("Section 80D - Medical Insurance (max ₹25,000)", min_value=0, max_value=50000, value=0, step=5000)
                    sec_80g = st.number_input("Section 80G - Donations", min_value=0, value=0, step=5000)
                
                with col2:
                    sec_80tta = st.number_input("Section 80TTA - Interest (max ₹10,000)", min_value=0, max_value=10000, value=0, step=1000)
                    sec_24 = st.number_input("Section 24 - Home Loan Interest (max ₹2,00,000)", min_value=0, max_value=200000, value=0, step=10000)
                    other_deductions = st.number_input("Other Deductions", min_value=0, value=0, step=5000)
        
        # Calculate button
        calculate_button = st.button(
            "Calculate Tax Liability",
            use_container_width=True
        )
        
        if calculate_button:
            # Calculate total income
            total_income = salary_income + business_income + capital_gains + house_property_income + other_income
            
            # Calculate deductions (only for old regime)
            total_deductions = 0
            if tax_regime == "Old Regime":
                total_deductions = sec_80c + sec_80d + sec_80g + sec_80tta + sec_24 + other_deductions
            
            # Calculate taxable income
            taxable_income = max(0, total_income - total_deductions)
            
            # Calculate tax based on regime
            tax_liability = calculate_tax(taxable_income, tax_regime)
            
            # Display results
            st.divider()
            st.subheader("Tax Calculation Results")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Income", f"₹{total_income:,.2f}")
            with col2:
                st.metric("Total Deductions", f"₹{total_deductions:,.2f}")
            with col3:
                st.metric("Taxable Income", f"₹{taxable_income:,.2f}")
            
            st.metric("Tax Liability", f"₹{tax_liability:,.2f}", delta=f"{tax_liability/total_income*100:.2f}% of Total Income")
            
            # Show tax breakdown
            st.markdown("**Tax Breakdown**")
            tax_breakdown = get_tax_breakdown(taxable_income, tax_regime)
            
            # Create a DataFrame for the tax breakdown
            df = pd.DataFrame(tax_breakdown)
            
            # Display as a table
            st.table(df)
            
            # Display as a chart
            fig = px.pie(df, values='Amount', names='Component', title='Tax Breakdown')
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 2: Tax Comparison
    with calc_tabs[1]:
        st.subheader("Tax Regime Comparison")
        st.write("Compare tax liability under old and new regimes to determine the most beneficial option.")
        
        # Income details for comparison
        with st.container(border=True):
            st.markdown("**Income Details**")
            
            col1, col2 = st.columns(2)
            with col1:
                comp_salary_income = st.number_input("Salary Income", min_value=0, value=500000, step=50000, key="comp_salary")
                comp_business_income = st.number_input("Business Income", min_value=0, value=0, step=10000, key="comp_business")
            
            with col2:
                comp_house_property_income = st.number_input("Income from House Property", min_value=-200000, value=0, step=10000, key="comp_house")
                comp_other_income = st.number_input("Other Income", min_value=0, value=0, step=10000, key="comp_other")
        
        # Deductions for comparison
        with st.container(border=True):
            st.markdown("**Deductions (applicable for Old Regime)**")
            
            col1, col2 = st.columns(2)
            with col1:
                comp_sec_80c = st.number_input("Section 80C", min_value=0, max_value=150000, value=50000, step=10000, key="comp_80c")
                comp_sec_80d = st.number_input("Section 80D", min_value=0, max_value=50000, value=25000, step=5000, key="comp_80d")
            
            with col2:
                comp_sec_24 = st.number_input("Home Loan Interest", min_value=0, max_value=200000, value=0, step=10000, key="comp_24")
                comp_other_deductions = st.number_input("Other Deductions", min_value=0, value=0, step=5000, key="comp_other_ded")
        
        # Compare button
        compare_button = st.button(
            "Compare Tax Regimes",
            use_container_width=True,
            key="compare_button"
        )
        
        if compare_button:
            # Calculate total income
            comp_total_income = comp_salary_income + comp_business_income + comp_house_property_income + comp_other_income
            
            # Calculate deductions for old regime
            comp_total_deductions = comp_sec_80c + comp_sec_80d + comp_sec_24 + comp_other_deductions
            
            # Calculate taxable income under both regimes
            old_taxable_income = max(0, comp_total_income - comp_total_deductions)
            new_taxable_income = comp_total_income
            
            # Calculate tax under both regimes
            old_tax = calculate_tax(old_taxable_income, "Old Regime")
            new_tax = calculate_tax(new_taxable_income, "New Regime")
            
            # Determine which regime is better
            tax_diff = old_tax - new_tax
            better_regime = "New Regime" if tax_diff > 0 else "Old Regime"
            
            # Display results
            st.divider()
            st.subheader("Comparison Results")
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Old Regime Tax", f"₹{old_tax:,.2f}", delta=f"Taxable Income: ₹{old_taxable_income:,.2f}")
            with col2:
                st.metric("New Regime Tax", f"₹{new_tax:,.2f}", delta=f"Taxable Income: ₹{new_taxable_income:,.2f}")
            
            st.success(f"**Recommendation:** {better_regime} is better for you, saving ₹{abs(tax_diff):,.2f}", icon="✅")
            
            # Show comparison chart
            comparison_data = {
                'Regime': ['Old Regime', 'New Regime'],
                'Tax': [old_tax, new_tax]
            }
            df_comp = pd.DataFrame(comparison_data)
            
            fig = px.bar(df_comp, x='Regime', y='Tax', title='Tax Comparison', color='Regime',
                         text_auto='.2s', labels={'Tax': 'Tax Liability (₹)'})
            st.plotly_chart(fig, use_container_width=True)
    
    # Tab 3: Deduction Analyzer
    with calc_tabs[2]:
        st.subheader("Deduction Analyzer")
        st.write("Analyze the impact of various deductions on your tax liability.")
        
        # Base income
        base_income = st.number_input("Total Income", min_value=0, value=1000000, step=100000)
        
        # Deduction scenarios
        with st.container(border=True):
            st.markdown("**Deduction Scenarios**")
            
            # Create a DataFrame to store deduction scenarios
            deduction_data = {
                'Deduction Type': ['No Deductions', 'Basic (80C only)', 'Standard', 'Maximum'],
                'Description': [
                    'No deductions claimed',
                    'Only Section 80C investments (₹1,50,000)',
                    'Section 80C + Medical Insurance + Home Loan Interest',
                    'Maximum possible deductions under all sections'
                ],
                '80C': [0, 150000, 150000, 150000],
                '80D': [0, 0, 25000, 50000],
                '24': [0, 0, 200000, 200000],
                'Other': [0, 0, 0, 100000]
            }
            df_deductions = pd.DataFrame(deduction_data)
            
            # Display the deduction scenarios
            st.table(df_deductions[['Deduction Type', 'Description']])
        
        # Analyze button
        analyze_button = st.button(
            "Analyze Deduction Impact",
            use_container_width=True,
            key="analyze_button"
        )
        
        if analyze_button:
            # Calculate tax for each scenario
            results = []
            for i, row in df_deductions.iterrows():
                total_deduction = row['80C'] + row['80D'] + row['24'] + row['Other']
                taxable_income = max(0, base_income - total_deduction)
                tax = calculate_tax(taxable_income, "Old Regime")
                
                results.append({
                    'Scenario': row['Deduction Type'],
                    'Total Deductions': total_deduction,
                    'Taxable Income': taxable_income,
                    'Tax Liability': tax,
                    'Tax Savings': calculate_tax(base_income, "Old Regime") - tax
                })
            
            # Create results DataFrame
            df_results = pd.DataFrame(results)
            
            # Display results
            st.divider()
            st.subheader("Deduction Impact Analysis")
            
            # Format the DataFrame for display
            df_display = df_results.copy()
            for col in ['Total Deductions', 'Taxable Income', 'Tax Liability', 'Tax Savings']:
                df_display[col] = df_display[col].apply(lambda x: f"₹{x:,.2f}")
            
            st.table(df_display)
            
            # Show tax savings chart
            fig = px.bar(df_results, x='Scenario', y='Tax Savings', title='Tax Savings by Deduction Scenario',
                         color='Scenario', text_auto='.2s', labels={'Tax Savings': 'Tax Savings (₹)'})
            st.plotly_chart(fig, use_container_width=True)
            
            # Show tax liability chart
            fig2 = px.bar(df_results, x='Scenario', y='Tax Liability', title='Tax Liability by Deduction Scenario',
                          color='Scenario', text_auto='.2s', labels={'Tax Liability': 'Tax Liability (₹)'})
            st.plotly_chart(fig2, use_container_width=True)

def calculate_tax(income, regime):
    """Calculate income tax based on income and regime."""
    tax = 0
    
    if regime == "Old Regime":
        # Old tax regime slabs
        if income <= 250000:
            tax = 0
        elif income <= 500000:
            tax = (income - 250000) * 0.05
        elif income <= 1000000:
            tax = 12500 + (income - 500000) * 0.2
        else:
            tax = 112500 + (income - 1000000) * 0.3
    else:
        # New tax regime slabs
        if income <= 300000:
            tax = 0
        elif income <= 600000:
            tax = (income - 300000) * 0.05
        elif income <= 900000:
            tax = 15000 + (income - 600000) * 0.1
        elif income <= 1200000:
            tax = 45000 + (income - 900000) * 0.15
        elif income <= 1500000:
            tax = 90000 + (income - 1200000) * 0.2
        else:
            tax = 150000 + (income - 1500000) * 0.3
    
    # Calculate cess
    cess = tax * 0.04
    
    return tax + cess

def get_tax_breakdown(income, regime):
    """Get a breakdown of tax components."""
    breakdown = []
    tax = 0
    
    if regime == "Old Regime":
        # Old tax regime slabs
        if income > 250000 and income <= 500000:
            slab_tax = (income - 250000) * 0.05
            breakdown.append({'Component': '5% on ₹2.5L to ₹5L', 'Amount': slab_tax})
            tax += slab_tax
        elif income > 500000:
            slab_tax = 250000 * 0.05
            breakdown.append({'Component': '5% on ₹2.5L to ₹5L', 'Amount': slab_tax})
            tax += slab_tax
        
        if income > 500000 and income <= 1000000:
            slab_tax = (income - 500000) * 0.2
            breakdown.append({'Component': '20% on ₹5L to ₹10L', 'Amount': slab_tax})
            tax += slab_tax
        elif income > 1000000:
            slab_tax = 500000 * 0.2
            breakdown.append({'Component': '20% on ₹5L to ₹10L', 'Amount': slab_tax})
            tax += slab_tax
        
        if income > 1000000:
            slab_tax = (income - 1000000) * 0.3
            breakdown.append({'Component': '30% on above ₹10L', 'Amount': slab_tax})
            tax += slab_tax
    else:
        # New tax regime slabs
        if income > 300000 and income <= 600000:
            slab_tax = (income - 300000) * 0.05
            breakdown.append({'Component': '5% on ₹3L to ₹6L', 'Amount': slab_tax})
            tax += slab_tax
        elif income > 600000:
            slab_tax = 300000 * 0.05
            breakdown.append({'Component': '5% on ₹3L to ₹6L', 'Amount': slab_tax})
            tax += slab_tax
        
        if income > 600000 and income <= 900000:
            slab_tax = (income - 600000) * 0.1
            breakdown.append({'Component': '10% on ₹6L to ₹9L', 'Amount': slab_tax})
            tax += slab_tax
        elif income > 900000:
            slab_tax = 300000 * 0.1
            breakdown.append({'Component': '10% on ₹6L to ₹9L', 'Amount': slab_tax})
            tax += slab_tax
        
        if income > 900000 and income <= 1200000:
            slab_tax = (income - 900000) * 0.15
            breakdown.append({'Component': '15% on ₹9L to ₹12L', 'Amount': slab_tax})
            tax += slab_tax
        elif income > 1200000:
            slab_tax = 300000 * 0.15
            breakdown.append({'Component': '15% on ₹9L to ₹12L', 'Amount': slab_tax})
            tax += slab_tax
        
        if income > 1200000 and income <= 1500000:
            slab_tax = (income - 1200000) * 0.2
            breakdown.append({'Component': '20% on ₹12L to ₹15L', 'Amount': slab_tax})
            tax += slab_tax
        elif income > 1500000:
            slab_tax = 300000 * 0.2
            breakdown.append({'Component': '20% on ₹12L to ₹15L', 'Amount': slab_tax})
            tax += slab_tax
        
        if income > 1500000:
            slab_tax = (income - 1500000) * 0.3
            breakdown.append({'Component': '30% on above ₹15L', 'Amount': slab_tax})
            tax += slab_tax
    
    # Add cess
    cess = tax * 0.04
    breakdown.append({'Component': 'Health & Education Cess (4%)', 'Amount': cess})
    
    return breakdown

# This function can be imported and used in the main application
if __name__ == "__main__":
    st.set_page_config(layout="wide", page_title="Tax Calculator")
    tax_calculator_tab()