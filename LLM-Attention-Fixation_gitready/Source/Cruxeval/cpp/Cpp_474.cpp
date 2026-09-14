#include<assert.h>
#include<bits/stdc++.h>

std::string f(std::string txt, int marker) {
    std::istringstream iss(txt);
    std::vector<std::string> lines;
    std::string line;
    while (std::getline(iss, line)) {
        lines.push_back(line);
    }

    std::vector<std::string> a;
    for (std::string line : lines) {
        std::string new_line = line;
        int spaces = marker - line.size();
        if (spaces > 0) {
            int left_spaces = spaces / 2;
            int right_spaces = spaces - left_spaces;
            new_line = std::string(left_spaces, ' ') + line + std::string(right_spaces, ' ');
        }
        a.push_back(new_line);
    }

    std::string result;
    for (std::string line : a) {
        result += line + '\n';
    }
    result.pop_back(); // remove the trailing '\n'

    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("#[)[]>[^e>\n 8"), (-5)) == ("#[)[]>[^e>\n 8"));
}
