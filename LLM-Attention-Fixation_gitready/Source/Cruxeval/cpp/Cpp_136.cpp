#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text, long width) {
    std::istringstream iss(text);
    std::vector<std::string> lines;
    for (std::string line; std::getline(iss, line); ) {
        std::string centered_line = std::string(width, ' ');
        centered_line.replace(width/2, line.length(), line);
        lines.push_back(centered_line);
    }
    std::string result;
    for (const auto& line : lines) {
        result += line + '\n';
    }
    result.pop_back();  // remove the last newline
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("a\nbc\n\nd\nef"), (5)) == ("  a  \n  bc \n     \n  d  \n  ef "));
}
