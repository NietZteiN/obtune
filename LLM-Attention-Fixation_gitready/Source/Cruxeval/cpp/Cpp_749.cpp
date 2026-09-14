#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long width) {
    std::string result = "";
    std::vector<std::string> lines;
    std::string line;
    std::istringstream iss(text);
    while (std::getline(iss, line, '\n')) {
        lines.push_back(line);
    }

    for (const auto& l : lines) {
        result += std::string((width - l.size()) / 2, ' ') + l + std::string((width - l.size() + 1) / 2, ' ');
        result += '\n';
    }

    result = result.substr(0, result.size() - 1); // Remove the very last empty line
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("l\nl"), (2)) == ("l \nl "));
}
