#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string ls = text;
    for (int i = 0; i < ls.length(); i++) {
        if (ls[i] != '+') {
            ls.insert(i, "+");
            ls.insert(i, "*");
            break;
        }
    }
    std::string result;
    for (int i = 0; i < ls.length(); i++) {
        result += ls[i];
        if (i != ls.length() - 1) {
            result += '+';
        }
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("nzoh")) == ("*+++n+z+o+h"));
}
