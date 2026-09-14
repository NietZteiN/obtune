#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string txt, std::string sep, long sep_count) {
    std::string o = "";
    while (sep_count > 0 && txt.find(sep) != std::string::npos) {
        size_t pos = txt.find_last_of(sep);
        o += txt.substr(0, pos + 1);
        txt = txt.substr(pos + 1);
        sep_count--;
    }
    return o + txt;
}
int main() {
    auto candidate = f;
    assert(candidate(("i like you"), (" "), (-1)) == ("i like you"));
}
