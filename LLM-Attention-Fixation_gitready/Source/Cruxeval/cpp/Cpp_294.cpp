#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string n, std::string m, std::string text) {
    if (text.empty() || (text.find_first_not_of(' ') == text.npos)) {
        return text;
    }
    std::string head = text.substr(0, 1), mid = text.substr(1, text.length() - 2), tail = text.substr(text.length() - 1);
    std::string joined = "";
    for (char c : head) {
        if (c == n[0]) {
            joined += m;
        } else {
            joined += c;
        }
    }
    for (char c : mid) {
        if (c == n[0]) {
            joined += m;
        } else {
            joined += c;
        }
    }
    for (char c : tail) {
        if (c == n[0]) {
            joined += m;
        } else {
            joined += c;
        }
    }
    return joined;
}
int main() {
    auto candidate = f;
    assert(candidate(("x"), ("$"), ("2xz&5H3*1a@#a*1hris")) == ("2$z&5H3*1a@#a*1hris"));
}
