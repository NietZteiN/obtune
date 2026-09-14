#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string ls = text;
    int total = (ls.length() - 1) * 2;
    for (int i = 1; i <= total; i++) {
        if (i % 2) {
            ls.push_back('+');
        } else {
            ls.insert(0, 1, '+');
        }
    }
    return ls;
}
int main() {
    auto candidate = f;
    assert(candidate(("taole")) == ("++++taole++++"));
}
