#include<assert.h>
#include<bits/stdc++.h>

std::string expandTabs(const std::string& str, int tabSize) {
    std::string result;
    int col = 0;
    for (char ch : str) {
        if (ch == '\t') {
            int spaces = tabSize - (col % tabSize);
            result.append(spaces, ' ');
            col += spaces;
        } else {
            result.push_back(ch);
            ++col;
        }
    }
    return result;
}

std::string f(std::string string) {
    int bigTab = 100;
    for (int i = 10; i < 30; ++i) {
        int tabCount = std::count(string.begin(), string.end(), '\t');
        if (0 < tabCount && tabCount < 20) {
            bigTab = i;
            break;
        }
    }
    return expandTabs(string, bigTab);
}
int main() {
    auto candidate = f;
    assert(candidate(("1  			3")) == ("1                             3"));
}
