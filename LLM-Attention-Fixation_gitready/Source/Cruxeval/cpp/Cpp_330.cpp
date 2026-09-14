#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string ans;
    for (char& c: text) {
        if (std::isdigit(c)) {
            ans += c;
        } else {
            ans += ' ';
        }
    }
    return ans;
}
int main() {
    auto candidate = f;
    assert(candidate(("m4n2o")) == (" 4 2 "));
}
