// Set the dimensions and margins of the graph
const margin = {top: 20, right: 20, bottom: 30, left: 40};
const width = 600 - margin.left - margin.right;
const height = 400 - margin.top - margin.bottom;

// Create the SVG container
const svg = d3.select("#visualization")
    .append("svg")
    .attr("width", width + margin.left + margin.right)
    .attr("height", height + margin.top + margin.bottom)
    .append("g")
    .attr("transform", `translate(${margin.left},${margin.top})`);

// Fetch data from Flask backend
async function fetchData() {
    try {
        const response = await fetch('http://127.0.0.1:5000/api/data');
        const data = await response.json();
        
        // Create scales
        const x = d3.scaleBand()
            .range([0, width])
            .padding(0.1);

        const y = d3.scaleLinear()
            .range([height, 0]);
            
        // Scale domains
        x.domain(data.map(d => d.id));
        y.domain([0, d3.max(data, d => d.value)]);

        // Add X axis
        svg.append("g")
            .attr("transform", `translate(0,${height})`)
            .call(d3.axisBottom(x));

        // Add Y axis
        svg.append("g")
            .call(d3.axisLeft(y));

        // Create bars
        svg.selectAll(".bar")
            .data(data)
            .enter()
            .append("rect")
            .attr("class", "bar")
            .attr("x", d => x(d.id))
            .attr("width", x.bandwidth())
            .attr("y", d => y(d.value))
            .attr("height", d => height - y(d.value));

    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

// Call the function when the page loads
fetchData();
