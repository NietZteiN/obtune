#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    for (int i = 0; i < text.size(); i++) {
        if (text.substr(0, i).find("two") == 0) {
            return text.substr(i);
        }
    }
    return "no";
}
int main() {
    auto candidate = f;
    assert(candidate(("2two programmers")) == ("no"));
}
