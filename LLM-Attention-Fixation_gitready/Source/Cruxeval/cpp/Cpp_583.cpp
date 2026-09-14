#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, std::string ch) {
    std::vector<std::string> result;
    std::stringstream ss(text);
    std::string line;
    while (std::getline(ss, line, '\n')) {
        if (!line.empty() && line[0] == ch[0]) {
            std::transform(line.begin(), line.end(), line.begin(), ::tolower);
            result.push_back(line);
        } else {
            std::transform(line.begin(), line.end(), line.begin(), ::toupper);
            result.push_back(line);
        }
    }
    
    return std::accumulate(result.begin(), result.end(), std::string(), 
        [](const std::string& a, const std::string& b) -> std::string { 
            return a + (a.empty() ? "" : "\n") + b; 
        });
}
int main() {
    auto candidate = f;
    assert(candidate(("t\nza\na"), ("t")) == ("t\nZA\nA"));
}
