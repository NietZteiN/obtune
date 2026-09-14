#include<assert.h>
#include<bits/stdc++.h>
long f(std::string text, std::string letter) {
    std::string t = text;
    for (char alph : text) {
        t.erase(std::remove(t.begin(), t.end(), alph), t.end());
    }
    return std::count(t.begin(), t.end(), *letter.c_str()) + 1;
}
int main() {
    auto candidate = f;
    assert(candidate(("c, c, c ,c, c"), ("c")) == (1));
}
