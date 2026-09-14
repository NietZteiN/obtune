#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string line, std::string character) {
    int count = std::count(line.begin(), line.end(), character[0]);
    for (int i = count + 1; i > 0; i--) {
        int length = line.length() + (i / character.length());
        int spaces = length - line.length();
        int padding_left = spaces / 2;
        int padding_right = spaces - padding_left;
        line = std::string(padding_left, character[0]) + line + std::string(padding_right, character[0]);
    }
    return line;
}
int main() {
    auto candidate = f;
    assert(candidate(("$78"), ("$")) == ("$$78$$"));
}
