"""
Visualization utilities with consistent styling.
All charts follow a unified color scheme and formatting.
"""
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


# Color scheme
COLORS = {
    'primary': '#1f77b4',      # Blue
    'secondary': '#ff7f0e',    # Orange
    'accent': '#2ca02c',       # Green
    'warning': '#d62728',      # Red
    'neutral': '#7f7f7f',      # Gray
    'gradient': ['#08519c', '#3182bd', '#6baed6', '#9ecae1', '#c6dbef'],
    'diverging': ['#d73027', '#fc8d59', '#fee090', '#e0f3f8', '#91bfdb', '#4575b4']
}


def create_line_chart(df, x, y, title, xlabel=None, ylabel=None, 
                      color=None, height=400, show_markers=True):
    """
    Create a styled line chart.
    
    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name(s) for y-axis (can be list)
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        color: Column for color grouping
        height: Chart height in pixels
        show_markers: Show data point markers
    
    Returns:
        plotly figure
    """
    if isinstance(y, str):
        y = [y]
    
    fig = go.Figure()
    
    if color:
        for group in df[color].unique():
            df_group = df[df[color] == group]
            for y_col in y:
                fig.add_trace(go.Scatter(
                    x=df_group[x],
                    y=df_group[y_col],
                    mode='lines+markers' if show_markers else 'lines',
                    name=f"{group}" if len(y) == 1 else f"{group} - {y_col}",
                    line=dict(width=2),
                    marker=dict(size=6)
                ))
    else:
        for i, y_col in enumerate(y):
            fig.add_trace(go.Scatter(
                x=df[x],
                y=df[y_col],
                mode='lines+markers' if show_markers else 'lines',
                name=y_col,
                line=dict(width=2, color=COLORS['gradient'][i % len(COLORS['gradient'])]),
                marker=dict(size=6)
            ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, weight='bold')),
        xaxis_title=xlabel or x,
        yaxis_title=ylabel or ', '.join(y),
        height=height,
        hovermode='x unified',
        template='plotly_white',
        font=dict(size=12),
        showlegend=True,
        legend=dict(orientation='h', yanchor='bottom', y=1.02, xanchor='right', x=1)
    )
    
    return fig


def create_bar_chart(df, x, y, title, xlabel=None, ylabel=None, 
                     color=None, orientation='v', height=400, text_auto=False):
    """
    Create a styled bar chart.
    
    Args:
        df: DataFrame with data
        x: Column name for x-axis (or y-axis if horizontal)
        y: Column name for y-axis (or x-axis if horizontal)
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        color: Column for color grouping
        orientation: 'v' for vertical, 'h' for horizontal
        height: Chart height in pixels
        text_auto: Show values on bars
    
    Returns:
        plotly figure
    """
    fig = px.bar(
        df, 
        x=x if orientation == 'v' else y,
        y=y if orientation == 'v' else x,
        color=color,
        orientation=orientation,
        title=title,
        text_auto=text_auto,
        height=height,
        color_discrete_sequence=COLORS['gradient']
    )
    
    fig.update_layout(
        xaxis_title=xlabel or (x if orientation == 'v' else y),
        yaxis_title=ylabel or (y if orientation == 'v' else x),
        template='plotly_white',
        font=dict(size=12),
        showlegend=True if color else False,
        title=dict(font=dict(size=16, weight='bold'))
    )
    
    if text_auto:
        fig.update_traces(texttemplate='%{text:.1f}', textposition='outside')
    
    return fig


def create_choropleth_map(df, locations, values, title, 
                          locationmode='geojson-id', geojson=None,
                          color_scale='Blues', height=600):
    """
    Create a choropleth map for French departments.
    
    Args:
        df: DataFrame with data
        locations: Column with location codes
        values: Column with values to map
        title: Map title
        locationmode: Location matching mode
        geojson: GeoJSON object for boundaries
        color_scale: Color scale name
        height: Map height in pixels
    
    Returns:
        plotly figure
    """
    fig = px.choropleth(
        df,
        locations=locations,
        color=values,
        locationmode=locationmode,
        geojson=geojson,
        color_continuous_scale=color_scale,
        title=title,
        height=height,
        hover_data=df.columns.tolist()
    )
    
    fig.update_geos(
        fitbounds="locations",
        visible=False
    )
    
    fig.update_layout(
        title=dict(font=dict(size=16, weight='bold')),
        template='plotly_white',
        font=dict(size=12)
    )
    
    return fig


def create_scatter_plot(df, x, y, title, xlabel=None, ylabel=None,
                       color=None, size=None, height=400, trendline=None):
    """
    Create a scatter plot.
    
    Args:
        df: DataFrame with data
        x: Column name for x-axis
        y: Column name for y-axis
        title: Chart title
        xlabel: X-axis label
        ylabel: Y-axis label
        color: Column for color grouping
        size: Column for bubble size
        height: Chart height in pixels
        trendline: Trendline type ('ols', 'lowess', etc.)
    
    Returns:
        plotly figure
    """
    fig = px.scatter(
        df,
        x=x,
        y=y,
        color=color,
        size=size,
        title=title,
        height=height,
        trendline=trendline,
        color_discrete_sequence=COLORS['gradient'],
        hover_data=df.columns.tolist()
    )
    
    fig.update_layout(
        xaxis_title=xlabel or x,
        yaxis_title=ylabel or y,
        template='plotly_white',
        font=dict(size=12),
        title=dict(font=dict(size=16, weight='bold'))
    )
    
    return fig


def create_histogram(df, x, title, nbins=30, xlabel=None, height=400):
    """
    Create a histogram.
    
    Args:
        df: DataFrame with data
        x: Column name for values
        title: Chart title
        nbins: Number of bins
        xlabel: X-axis label
        height: Chart height in pixels
    
    Returns:
        plotly figure
    """
    fig = px.histogram(
        df,
        x=x,
        nbins=nbins,
        title=title,
        height=height,
        color_discrete_sequence=[COLORS['primary']]
    )
    
    fig.update_layout(
        xaxis_title=xlabel or x,
        yaxis_title='Count',
        template='plotly_white',
        font=dict(size=12),
        title=dict(font=dict(size=16, weight='bold')),
        showlegend=False
    )
    
    return fig


def create_box_plot(df, y, x=None, title='', ylabel=None, height=400):
    """
    Create a box plot.
    
    Args:
        df: DataFrame with data
        y: Column name for values
        x: Column name for grouping (optional)
        title: Chart title
        ylabel: Y-axis label
        height: Chart height in pixels
    
    Returns:
        plotly figure
    """
    fig = px.box(
        df,
        y=y,
        x=x,
        title=title,
        height=height,
        color_discrete_sequence=[COLORS['primary']]
    )
    
    fig.update_layout(
        yaxis_title=ylabel or y,
        template='plotly_white',
        font=dict(size=12),
        title=dict(font=dict(size=16, weight='bold'))
    )
    
    return fig


def create_heatmap(df, title, height=500, color_scale='RdYlBu_r'):
    """
    Create a heatmap.
    
    Args:
        df: DataFrame (will be used as-is for heatmap)
        title: Chart title
        height: Chart height in pixels
        color_scale: Color scale name
    
    Returns:
        plotly figure
    """
    fig = go.Figure(data=go.Heatmap(
        z=df.values,
        x=df.columns,
        y=df.index,
        colorscale=color_scale,
        hoverongaps=False
    ))
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=16, weight='bold')),
        height=height,
        template='plotly_white',
        font=dict(size=12)
    )
    
    return fig


def create_treemap(df, path, values, title, height=600):
    """
    Create a treemap visualization.
    
    Args:
        df: DataFrame with data
        path: List of columns defining hierarchy
        values: Column with values
        title: Chart title
        height: Chart height in pixels
    
    Returns:
        plotly figure
    """
    fig = px.treemap(
        df,
        path=path,
        values=values,
        title=title,
        height=height,
        color_continuous_scale='Blues'
    )
    
    fig.update_layout(
        title=dict(font=dict(size=16, weight='bold')),
        template='plotly_white',
        font=dict(size=12)
    )
    
    return fig


def create_metric_card(value, label, delta=None, delta_color='normal'):
    """
    Create formatted metric display.
    
    Args:
        value: Metric value
        label: Metric label
        delta: Change value (optional)
        delta_color: 'normal', 'inverse', or 'off'
    
    Returns:
        dict: Formatted metric data
    """
    return {
        'value': value,
        'label': label,
        'delta': delta,
        'delta_color': delta_color
    }


def format_number(num, suffix='', decimals=0):
    """
    Format large numbers with K/M suffixes.
    
    Args:
        num: Number to format
        suffix: Unit suffix (e.g., '%')
        decimals: Decimal places
    
    Returns:
        str: Formatted number
    """
    if pd.isna(num):
        return 'N/A'
    
    if abs(num) >= 1_000_000:
        return f"{num/1_000_000:.{decimals}f}M{suffix}"
    elif abs(num) >= 1_000:
        return f"{num/1_000:.{decimals}f}K{suffix}"
    else:
        return f"{num:.{decimals}f}{suffix}"
