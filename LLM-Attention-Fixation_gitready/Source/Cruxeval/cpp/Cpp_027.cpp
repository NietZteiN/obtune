#include<assert.h>
#include<bits/stdc++.h>
bool f(std::string w) {
    std::vector<char> ls(w.begin(), w.end());
    std::string omw = "";
    while (ls.size() > 0) {
        omw += ls[0];
        ls.erase(ls.begin());
        if (ls.size() * 2 > w.length()) {
            return w.substr(ls.size()) == omw;
        }
    }
    return false;
}
int main() {
    auto candidate = f;
    assert(candidate(("flak")) == (false));
}
