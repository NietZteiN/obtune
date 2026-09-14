#include<assert.h>
#include<bits/stdc++.h>

std::string f(std::string s) {
    std::string sep = ".";
    if (s.find(sep) == std::string::npos) {
        std::string result = "";
        for (char& c : s) {
            result += ", " + std::string(1, c);
        }
        return result + ", ";
    }
    std::string left = s.substr(0, s.find(sep));
    std::string right = s.substr(s.find(sep) + 1);
    std::string new_str = right + sep + left;
    sep = new_str.substr(new_str.find(sep), new_str.find(sep) + 1);
    
    size_t start_pos = 0;
    while((start_pos = new_str.find(sep, start_pos)) != std::string::npos) {
        new_str.replace(start_pos, sep.length(), ", ");
        start_pos += sep.length();
    }
    return ", " + new_str + ", ";
}
int main() {
    auto candidate = f;
    assert(candidate(("galgu")) == (", g, a, l, g, u, "));
}
