"""
GDP ANALYSIS PROJECT - Phiên bản OOP (Tất cả trong một file)

Cấu trúc:
1. Imports: Tất cả thư viện cần thiết.
2. Constants: Các hằng số (OUTPUT_DIR, etc.)
3. Lớp GDPAnalyzer: Chịu trách nhiệm tải, dọn dẹp và tính toán.
4. Lớp GDPVisualizer: Chịu trách nhiệm vẽ biểu đồ.
5. Lớp GDPReportGenerator: Chịu trách nhiệm xuất file (Excel, .txt).
6. Hàm main(): Điều phối, khởi tạo và gọi các lớp trên.
7. Khối `if __name__ == "__main__":` để thực thi.
"""

# Standard library imports
import sys
from datetime import datetime
from pathlib import Path

# Third-party imports
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import kagglehub

# ==================== CẤU HÌNH & HẰNG SỐ ====================

OUTPUT_DIR = "final_output"
START_YEAR = 1975
END_YEAR = 2025

# ==================== LỚP 1: DỊCH VỤ PHÂN TÍCH ====================

class GDPAnalyzer:
    """
    Chịu trách nhiệm tải, làm sạch và phân tích dữ liệu GDP.
    Lớp này không biết về visualization hay reporting.
    """
    def __init__(self):
        print("Khởi tạo GDPAnalyzer...")
        csv_path = self._download_data()
        self.df = self._load_data(csv_path)
        self.df_clean = self._clean_data()
        self.year_cols = [col for col in self.df_clean.columns if col.isdigit() and 1975 <= int(col) <= 2025]

    def _download_data(self):
        """Tải dataset GDP từ KaggleHub."""
        print("📥 Đang tải dataset từ KaggleHub...")
        try:
            path = kagglehub.dataset_download("codebynadiia/gdp-1975-2025")
            # Tìm file CSV đầu tiên trong thư mục đã giải nén
            csv_file = next(Path(path).rglob('*.csv'), None)
            
            if csv_file:
                print(f"✅ Đã tải và sử dụng file: {csv_file.name}")
                return csv_file
            else:
                raise FileNotFoundError("Không tìm thấy file CSV trong dataset")
        except Exception as e:
            print(f"❌ Lỗi khi tải dataset: {e}")
            raise

    def _load_data(self, csv_path):
        """Load dữ liệu GDP từ file CSV."""
        print(f"📂 Đang load dữ liệu từ: {csv_path}")
        df = pd.read_csv(csv_path)
        print(f"✅ Đã load {len(df)} dòng, {len(df.columns)} cột")
        return df

    def _clean_data(self):
        """Làm sạch dữ liệu GDP: loại bỏ NaN Country và quốc gia thiếu quá nhiều data."""
        print("🧹 Đang làm sạch dữ liệu...")
        
        # Bước 1: Loại bỏ dòng không có tên quốc gia
        df_clean = self.df[self.df['Country'].notna()].copy()
        initial_count = len(df_clean)
        
        # Bước 2: Loại bỏ khoảng trắng thừa trong tên quốc gia
        df_clean['Country'] = df_clean['Country'].str.strip()
        
        # Bước 3: Loại bỏ các quốc gia có quá nhiều năm thiếu data (>80%)
        year_cols = [col for col in df_clean.columns if col.isdigit()]
        missing_pct = df_clean[year_cols].isna().sum(axis=1) / len(year_cols) * 100
        
        # Lấy danh sách các quốc gia bị loại
        removed_countries = df_clean[missing_pct > 80]['Country'].tolist()
        if removed_countries:
            print(f"   ⚠️  Loại bỏ {len(removed_countries)} quốc gia thiếu >80% data:")
            print(f"      {', '.join(removed_countries[:5])}" + 
                  (f" và {len(removed_countries)-5} quốc gia khác" if len(removed_countries) > 5 else ""))
        
        # Áp dụng filter
        df_clean = df_clean[missing_pct <= 80].copy()
        
        final_count = len(df_clean)
        removed_total = initial_count - final_count
        
        print(f"✅ Đã làm sạch: {final_count} records hợp lệ (loại bỏ {removed_total} records)")
        return df_clean

    def get_top_countries(self, year=2025, n=15):
        """Lấy danh sách N quốc gia GDP cao nhất."""
        year_col = str(year)
        if year_col not in self.df_clean.columns:
            return []
        return self.df_clean[self.df_clean[year_col].notna()].nlargest(n, year_col)['Country'].tolist()

    def run_descriptive_analysis(self):
        """Thực hiện phân tích thống kê mô tả. Trả về một dict kết quả."""
        print("📊 Đang chạy Phân tích Thống Kê Mô tả...")
        stats_results = {}
        
        # 1. Thống kê 2025
        year_2025 = self.df_clean['2025'].dropna()
        stats_2025 = {
            'count': len(year_2025), 'mean': year_2025.mean(),
            'median': year_2025.median(), 'std': year_2025.std(),
            'min': year_2025.min(), 'max': year_2025.max(),
            'q25': year_2025.quantile(0.25), 'q75': year_2025.quantile(0.75),
            'min_country': self.df_clean[self.df_clean['2025'] == year_2025.min()]['Country'].values[0],
            'max_country': self.df_clean[self.df_clean['2025'] == year_2025.max()]['Country'].values[0]
        }
        stats_results['2025'] = stats_2025

        # 2. Phân nhóm GDP
        def categorize_gdp(gdp_value):
            gdp_billion = gdp_value / 1e3
            if gdp_billion >= 10000: return 'Siêu lớn (≥$10,000B)'
            elif gdp_billion >= 3000: return 'Lớn ($3,000-10,000B)'
            elif gdp_billion >= 1000: return 'Trung bình ($1,000-3,000B)'
            else: return 'Nhỏ (<$1,000B)'
        
        df_2025 = self.df_clean[self.df_clean['2025'].notna()].copy()
        df_2025['GDP_Category'] = df_2025['2025'].apply(categorize_gdp)
        stats_results['categories'] = df_2025['GDP_Category'].value_counts().to_dict()

        # 3. CAGR
        def calculate_cagr(start_value, end_value, years):
            if pd.isna(start_value) or pd.isna(end_value) or start_value <= 0: return None
            return ((end_value / start_value) ** (1/years) - 1) * 100
        
        df_growth = self.df_clean[(self.df_clean['1975'].notna()) & (self.df_clean['2025'].notna())].copy()
        df_growth['CAGR'] = df_growth.apply(
            lambda row: calculate_cagr(row['1975'], row['2025'], 50), axis=1
        )
        stats_results['cagr_top'] = df_growth.nlargest(5, 'CAGR')[['Country', 'CAGR', '1975', '2025']].to_dict('records')
        stats_results['cagr_bottom'] = df_growth.nsmallest(5, 'CAGR')[['Country', 'CAGR', '1975', '2025']].to_dict('records')

        # 4. Xu hướng thập kỷ
        decades = [1975, 1985, 1995, 2005, 2015, 2025]
        decade_stats = []
        for year in decades:
            if str(year) in self.df_clean.columns:
                year_data = self.df_clean[str(year)].dropna()
                decade_stats.append({
                    'year': year, 'total_gdp': year_data.sum(),
                    'avg_gdp': year_data.mean(), 'count': len(year_data)
                })
        stats_results['decades'] = decade_stats

        # 5. Chênh lệch
        top_10_gdp = df_2025.nlargest(10, '2025')['2025'].sum()
        total_gdp = df_2025['2025'].sum()
        top_10_percentage = (top_10_gdp / total_gdp) * 100
        
        sorted_gdp = df_2025['2025'].sort_values().values
        n = len(sorted_gdp)
        cumsum = sorted_gdp.cumsum()
        gini = (2 * sum((i+1) * sorted_gdp[i] for i in range(n))) / (n * cumsum[-1]) - (n + 1) / n
        stats_results['inequality'] = {'top_10_percentage': top_10_percentage, 'gini': gini}
        
        print("✅ Phân tích Thống Kê Mô tả hoàn tất.")
        return stats_results

    def run_top_10_analysis(self, year=2025):
        """Phân tích top 10 quốc gia GDP cao nhất. Trả về DataFrame."""
        print(f"📊 Đang chạy Phân tích Top 10 GDP {year}...")
        year_col = str(year)
        if year_col not in self.df_clean.columns:
            print(f"⚠️ Không có dữ liệu cho năm {year}")
            return pd.DataFrame()
        
        top_10 = self.df_clean[self.df_clean[year_col].notna()].nlargest(10, year_col)[['Country', year_col]].copy()
        top_10.columns = ['Country', 'GDP']
        print("✅ Phân tích Top 10 hoàn tất.")
        return top_10

    def run_growth_analysis(self, countries, start_year=1975, end_year=2025):
        """Phân tích tăng trưởng của các quốc gia. Trả về dict."""
        print(f"📊 Đang chạy Phân tích Tăng trưởng ({start_year}-{end_year})...")
        growth_data = {}
        years = list(range(start_year, end_year + 1))
        # Chỉ lấy các cột năm thực sự có trong dataframe
        year_cols = [str(y) for y in years if str(y) in self.df_clean.columns]
        
        # Lọc df một lần để tăng hiệu suất
        df_filtered = self.df_clean[self.df_clean['Country'].isin(countries)]
        
        for country in countries:
            country_row = df_filtered[df_filtered['Country'] == country]
            if country_row.empty:
                continue
            
            # Dùng .get() để tránh lỗi nếu cột năm không tồn tại
            country_gdp = {
                int(year_col): country_row[year_col].values[0] 
                for year_col in year_cols 
                if pd.notna(country_row[year_col].values[0])
            }
            if country_gdp:
                growth_data[country] = country_gdp
                
        print(f"✅ Phân tích Tăng trưởng cho {len(growth_data)} quốc gia hoàn tất.")
        return growth_data

# ==================== LỚP 2: DỊCH VỤ HIỂN THỊ ====================

class GDPVisualizer:
    """
    Chịu trách nhiệm tạo tất cả các biểu đồ.
    Nhận dữ liệu đã xử lý và lưu file ảnh.
    """
    def __init__(self, output_dir_str):
        self.output_dir = Path(output_dir_str)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        plt.style.use('seaborn-v0_8-darkgrid')
        sns.set_palette("husl")
        print(f"Khởi tạo GDPVisualizer. Kết quả sẽ được lưu vào: {self.output_dir}")

    def _save_plot(self, fig, filename):
        """Helper để lưu biểu đồ."""
        output_path = self.output_dir / filename
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close(fig)
        print(f"✅ Đã lưu biểu đồ: {output_path}")

    def plot_descriptive_stats(self, stats_results, df):
        """Tạo 4 biểu đồ thống kê mô tả."""
        print("📈 Đang tạo biểu đồ Thống Kê Mô tả...")
        fig, axes = plt.subplots(2, 2, figsize=(18, 12))
        fig.suptitle('Phân Tích Thống Kê GDP', fontsize=18, fontweight='bold', y=0.995)

        # 1. GDP Việt Nam (1975-2025)
        ax1 = axes[0, 0]
        vietnam_row = df[df['Country'] == 'Vietnam']
        if not vietnam_row.empty:
            years = [int(col) for col in df.columns if col.isdigit() and 1975 <= int(col) <= 2025]
            vietnam_gdp = []
            available_years = []
            
            for year in years:
                year_col = str(year)
                if year_col in df.columns:
                    gdp_value = vietnam_row[year_col].values[0]
                    if pd.notna(gdp_value):
                        vietnam_gdp.append(gdp_value / 1e3)  # Convert to Billion USD
                        available_years.append(year)
            
            if vietnam_gdp:
                ax1.plot(available_years, vietnam_gdp, marker='o', linewidth=2.5, color='#e74c3c', markersize=5, alpha=0.8)
                ax1.fill_between(available_years, vietnam_gdp, alpha=0.3, color='#e74c3c')
                ax1.set_xlabel('Năm', fontsize=12, fontweight='bold')
                ax1.set_ylabel('GDP (Billion USD)', fontsize=12, fontweight='bold')
                ax1.set_title('GDP Việt Nam (1975-2025)', fontsize=14, fontweight='bold', pad=15)
                ax1.grid(True, alpha=0.3)
                
                # Thêm annotation cho điểm đầu và cuối
                ax1.annotate(f'${vietnam_gdp[0]:.1f}B', 
                            xy=(available_years[0], vietnam_gdp[0]),
                            xytext=(10, 10), textcoords='offset points',
                            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                            fontsize=9, fontweight='bold')
                ax1.annotate(f'${vietnam_gdp[-1]:.1f}B', 
                            xy=(available_years[-1], vietnam_gdp[-1]),
                            xytext=(10, -15), textcoords='offset points',
                            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.7),
                            fontsize=9, fontweight='bold')
        else:
            ax1.text(0.5, 0.5, 'Không tìm thấy dữ liệu Việt Nam', 
                    ha='center', va='center', fontsize=12, transform=ax1.transAxes)

        # 2. Pie Chart
        ax2 = axes[0, 1]
        if 'categories' in stats_results:
            categories = stats_results['categories']
            order = ['Siêu lớn (≥$10,000B)', 'Lớn ($3,000-10,000B)', 'Trung bình ($1,000-3,000B)', 'Nhỏ (<$1,000B)']
            labels = [cat for cat in order if cat in categories]
            sizes = [categories[cat] for cat in labels]
            
            colors = ['#ff6b6b', '#4ecdc4', '#45b7d1', '#96ceb4']
            explode = (0.05, 0.05, 0.05, 0)
            
            wedges, _ = ax2.pie(sizes, colors=colors, startangle=90, explode=explode)
            legend_labels = [f'{s/sum(sizes)*100:.1f}% - {l} ({s} quốc gia)' for l, s in zip(labels, sizes)]
            ax2.legend(wedges, legend_labels, title="Phân Loại", loc="center left", bbox_to_anchor=(1, 0, 0.5, 1))
            ax2.set_title('Phân Nhóm Theo Quy Mô GDP 2025', fontsize=14, fontweight='bold', pad=15)

        # 3. Bar Chart - Top 5 nhanh
        ax3 = axes[1, 0]
        if 'cagr_top' in stats_results:
            top_growth = stats_results['cagr_top'][:5]
            countries = [r['Country'] for r in top_growth]
            cagr_values = [r['CAGR'] for r in top_growth]
            
            bars = ax3.barh(countries, cagr_values, color='#2ecc71', alpha=0.8, edgecolor='black')
            ax3.set_xlabel('CAGR (%/năm)', fontsize=12, fontweight='bold')
            ax3.set_title('Top 5 Tăng Trưởng NHANH Nhất', fontsize=14, fontweight='bold', pad=15)
            ax3.invert_yaxis()
            for bar in bars:
                width = bar.get_width()
                ax3.text(width + 0.2, bar.get_y() + bar.get_height()/2, f'{width:.2f}%', ha='left', va='center')

        # 4. Bar Chart - Top 5 chậm
        ax4 = axes[1, 1]
        if 'cagr_bottom' in stats_results:
            bottom_growth = stats_results['cagr_bottom'][:5]
            countries = [r['Country'] for r in bottom_growth]
            cagr_values = [r['CAGR'] for r in bottom_growth]
            
            bars = ax4.barh(countries, cagr_values, color='#e74c3c', alpha=0.8, edgecolor='black')
            ax4.set_xlabel('CAGR (%/năm)', fontsize=12, fontweight='bold')
            ax4.set_title('Top 5 Tăng Trưởng CHẬM Nhất', fontsize=14, fontweight='bold', pad=15)
            ax4.invert_yaxis()
            for bar in bars:
                width = bar.get_width()
                ax4.text(width + 0.05, bar.get_y() + bar.get_height()/2, f'{width:.2f}%', ha='left', va='center')
    
        fig.tight_layout()
        self._save_plot(fig, 'statistical_analysis.png')

    def plot_top_10(self, top_10_df, year=2025):
        """Vẽ biểu đồ bar chart cho Top 10 GDP."""
        if top_10_df.empty: return
        print(f"📈 Đang tạo biểu đồ Top 10 GDP {year}...")
        
        fig, ax = plt.subplots(figsize=(14, 8))
        colors = sns.color_palette('viridis', len(top_10_df))
        bars = ax.barh(top_10_df['Country'], top_10_df['GDP'] / 1e3, color=colors, edgecolor='black')
        
        for bar in bars:
            width = bar.get_width()
            ax.text(width, bar.get_y() + bar.get_height() / 2, f' ${width:.0f}B', ha='left', va='center')
        
        ax.set_xlabel('GDP (Billion USD)', fontsize=12, fontweight='bold')
        ax.set_title(f'Top 10 Countries by GDP ({year})', fontsize=16, fontweight='bold', pad=20)
        ax.invert_yaxis()
        ax.grid(True, axis='x', alpha=0.3)
        ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.0f}B'))
        
        fig.tight_layout()
        self._save_plot(fig, f'top_10_gdp_{year}.png')

    def plot_growth(self, growth_data, start_year, end_year):
        """Vẽ biểu đồ line chart cho Growth Analysis."""
        if not growth_data: return
        print(f"📈 Đang tạo biểu đồ Growth Analysis...")
        
        fig, ax = plt.subplots(figsize=(16, 10))
        
        for country, country_data in growth_data.items():
            sorted_years = sorted(country_data.keys())
            gdp_values = [country_data[year] / 1e3 for year in sorted_years] # Convert to Billion
            ax.plot(sorted_years, gdp_values, marker='o', linewidth=2.5, label=country, alpha=0.8)
        
        ax.set_xlabel('Year', fontsize=12, fontweight='bold')
        ax.set_ylabel('GDP (Billion USD)', fontsize=12, fontweight='bold')
        ax.set_title(f'GDP Growth Analysis ({start_year}-{end_year})', fontsize=16, fontweight='bold', pad=20)
        ax.legend(loc='best', fontsize=11)
        ax.grid(True, alpha=0.3)
        ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'${x:.0f}B'))
        
        fig.tight_layout()
        self._save_plot(fig, f'gdp_growth_{start_year}-{end_year}.png')


# ==================== LỚP 3: DỊCH VỤ BÁO CÁO ====================

class GDPReportGenerator:
    """
    Chịu trách nhiệm xuất kết quả phân tích ra file (Excel, text).
    """
    def __init__(self, output_dir_str):
        self.output_dir = Path(output_dir_str)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        print(f"Khởi tạo GDPReportGenerator. Báo cáo sẽ được lưu vào: {self.output_dir}")

    def export_descriptive_report(self, stats_results, df):
        """Xuất báo cáo thống kê ra file Excel và text."""
        print("💾 Đang xuất báo cáo thống kê...")
        
        # 1. Xuất Excel
        excel_path = self.output_dir / 'statistical_report.xlsx'
        try:
            with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
                pd.DataFrame([stats_results['2025']]).to_excel(writer, sheet_name='Summary 2025', index=False)
                if 'categories' in stats_results:
                    pd.DataFrame(list(stats_results['categories'].items()), columns=['Category', 'Count']).to_excel(writer, sheet_name='GDP Categories', index=False)
                if 'cagr_top' in stats_results:
                    pd.DataFrame(stats_results['cagr_top']).to_excel(writer, sheet_name='Top Growth', index=False)
                if 'cagr_bottom' in stats_results:
                    pd.DataFrame(stats_results['cagr_bottom']).to_excel(writer, sheet_name='Slow Growth', index=False)
                if 'decades' in stats_results:
                    pd.DataFrame(stats_results['decades']).to_excel(writer, sheet_name='Decades Trend', index=False)
            print(f"✅ Đã xuất: {excel_path}")
        except Exception as e:
            print(f"❌ Lỗi khi xuất Excel: {e}")

        # 2. Xuất text report
        text_path = self.output_dir / 'statistical_insights.txt'
        try:
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write("="*80 + "\n   BÁO CÁO PHÂN TÍCH THỐNG KÊ GDP (1975-2025)\n" + "="*80 + "\n\n")
                f.write("KEY INSIGHTS:\n" + "-" * 60 + "\n")
                
                if 'inequality' in stats_results:
                    f.write(f"1. Top 10 quốc gia chiếm {stats_results['inequality']['top_10_percentage']:.1f}% GDP thế giới\n")
                    f.write(f"2. Hệ số Gini: {stats_results['inequality']['gini']:.3f} (cao → bất bình đẳng)\n\n")
                
                f.write("3. Các nước tăng trưởng nhanh:\n")
                for record in stats_results.get('cagr_top', [])[:3]:
                    f.write(f"   - {record['Country']}: {record['CAGR']:.2f}%/năm\n")
                
                f.write("\n4. GDP trung bình toàn cầu tăng từ:\n")
                decades = stats_results.get('decades', [])
                if len(decades) >= 2:
                    first, last = decades[0], decades[-1]
                    f.write(f"   - {first['year']}: ${first['avg_gdp']/1e3:.2f}B (trên {first['count']} quốc gia)\n")
                    f.write(f"   - {last['year']}: ${last['avg_gdp']/1e3:.2f}B (trên {last['count']} quốc gia)\n")
                    f.write(f"   - Tăng gấp: {last['avg_gdp'] / first['avg_gdp']:.1f} lần\n")
            print(f"✅ Đã xuất: {text_path}")
        except Exception as e:
            print(f"❌ Lỗi khi xuất file text: {e}")

    def export_top_10_excel(self, top_10_df, year=2025):
        """Xuất Top 10 ra file Excel."""
        if top_10_df.empty: return
        print(f"💾 Đang xuất Top 10 ra Excel...")
        
        output_path = self.output_dir / f'top_10_gdp_{year}.xlsx'
        export_df = top_10_df.copy()
        export_df.columns = ['Country', 'GDP (USD)']
        export_df['Year'] = year
        
        try:
            export_df.to_excel(output_path, sheet_name='GDP Data', index=False)
            print(f"✅ Đã xuất: {output_path}")
        except Exception as e:
            print(f"❌ Lỗi khi xuất Top 10 Excel: {e}")

# ==================== HÀM MAIN (ĐIỀU PHỐI) ====================

def main():
    """
    Hàm main - Điều phối (orchestrate) toàn bộ workflow.
    Đây là "Composition Root", nơi các đối tượng được tạo ra và kết nối.
    """
    print("="*80)
    print("   GDP ANALYSIS PROJECT    ")
    print("="*80)
    print(f"Thời gian: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    try:
        # ==================== 1. Khởi tạo (Composition) ====================
        # Khởi tạo các dịch vụ
        analyzer = GDPAnalyzer()
        visualizer = GDPVisualizer(OUTPUT_DIR)
        reporter = GDPReportGenerator(OUTPUT_DIR)

        # ==================== 2. Bước 1: Phân tích Thống kê Mô tả ====================
        print("\n" + "="*80)
        print("   BƯỚC 1: PHÂN TÍCH THỐNG KÊ & INSIGHTS")
        print("="*80)
        
        stats_results = analyzer.run_descriptive_analysis()
        visualizer.plot_descriptive_stats(stats_results, analyzer.df_clean)
        reporter.export_descriptive_report(stats_results, analyzer.df_clean)

        # ==================== 3. Bước 2: Phân tích Top 10 GDP 2025 ====================
        print("\n" + "="*80)
        print(f"   BƯỚC 2: PHÂN TÍCH #1: TOP 10 GDP {END_YEAR}")
        print("="*80)
        
        top_10 = analyzer.run_top_10_analysis(year=END_YEAR)
        visualizer.plot_top_10(top_10, year=END_YEAR)
        reporter.export_top_10_excel(top_10, year=END_YEAR)

        # ==================== 4. Bước 3: Phân tích Tăng trưởng ====================
        print("\n" + "="*80)
        print(f"   BƯỚC 3: PHÂN TÍCH #2: GDP GROWTH ANALYSIS ({START_YEAR}-{END_YEAR})")
        print("="*80)
        
        top_15_countries = analyzer.get_top_countries(year=END_YEAR, n=15)
        print(f"📋 Top 15 quốc gia: {', '.join(top_15_countries[:5])}... (và 10 quốc gia khác)")
        
        growth_data = analyzer.run_growth_analysis(top_15_countries, START_YEAR, END_YEAR)
        visualizer.plot_growth(growth_data, START_YEAR, END_YEAR)
        
        # ==================== 5. Hoàn tất ====================
        print("\n" + "="*80)
        print("   ✅ HOÀN TẤT TẤT CẢ PHÂN TÍCH VÀ BÁO CÁO")
        print("="*80)
        print(f"\n🎉 SUCCESS! Kiểm tra thư mục '{OUTPUT_DIR}/' để xem kết quả.")

    except Exception as e:
        print(f"\n❌ LỖI NGHIÊM TRỌNG TRONG QUÁ TRÌNH CHẠY: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

# ==================== ĐIỂM THỰC THI ====================

if __name__ == "__main__":
    main()
