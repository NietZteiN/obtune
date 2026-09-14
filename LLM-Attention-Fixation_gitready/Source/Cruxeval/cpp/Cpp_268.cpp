#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, std::string separator) {
    for (size_t i = 0; i < s.length(); i++) {
        if (s[i] == separator[0]) {
            std::string new_s = s;
            new_s[i] = '/';
            std::string result = "";
            for (char& c : new_s) {
                result += c;
                result += ' ';
            }
            result.pop_back(); // remove the trailing space
            return result;
        }
    }
    return NULL;
}
int main() {
    auto candidate = f;
    assert(candidate(("h grateful k"), (" ")) == ("h / g r a t e f u l   k"));
}
