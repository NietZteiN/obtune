#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string chars) {
    std::string s = "";
    for (char ch : chars) {
        if (std::count(chars.begin(), chars.end(), ch) % 2 == 0) {
            s += toupper(ch);
        } else {
            s += ch;
        }
    }
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate(("acbced")) == ("aCbCed"));
}
