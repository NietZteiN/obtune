#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::vector<char> ls(text.begin(), text.end());
    for(int x = ls.size() - 1; x >= 0; x--) {
        if(ls.size() <= 1) break;
        if(std::find("zyxwvutsrqponmlkjihgfedcba", "zyxwvutsrqponmlkjihgfedcba" + 26, ls[x]) == "zyxwvutsrqponmlkjihgfedcba" + 26) {
            ls.erase(ls.begin() + x);
        }
    }
    return std::string(ls.begin(), ls.end());
}
int main() {
    auto candidate = f;
    assert(candidate(("qq")) == ("qq"));
}
