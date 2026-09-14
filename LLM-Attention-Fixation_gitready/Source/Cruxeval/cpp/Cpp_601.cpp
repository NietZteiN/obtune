#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    int t = 5;
    std::string tab = "";
    for (char i : text) {
        if (strchr("aeiouyAEIOUY", i)) {
            tab += std::string(t, std::toupper(i));
        } else {
            tab += std::string(t, i);
        }
        tab += " ";
    }
    // remove last space
    tab.pop_back();
    return tab;
}
int main() {
    auto candidate = f;
    assert(candidate(("csharp")) == ("ccccc sssss hhhhh AAAAA rrrrr ppppp"));
}
