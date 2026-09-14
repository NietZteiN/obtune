#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string code) {
    std::stringstream ss(code);
    std::string line;
    std::vector<std::string> result;
    int level = 0;
    while (std::getline(ss, line, ']')) {
        level += std::count(line.begin(), line.end(), '{') - std::count(line.begin(), line.end(), '}');
        result.push_back(line.substr(0, 1) + " " + std::string(2 * level, ' ') + line.substr(1));
    }
    return std::accumulate(result.begin(), result.end(), std::string(),
                           [](const std::string& a, const std::string& b) -> std::string {
                               return a + (a.empty() ? "" : "\n") + b;
                           });
}
int main() {
    auto candidate = f;
    assert(candidate(("if (x) {y = 1;} else {z = 1;}")) == ("i f (x) {y = 1;} else {z = 1;}"));
}
