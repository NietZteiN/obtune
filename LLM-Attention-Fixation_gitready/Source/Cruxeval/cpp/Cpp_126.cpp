#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string s = text;
    std::string::size_type i = s.rfind('o');

    if (i == std::string::npos) {
        return "-" + s;
    }

    std::string div = s.substr(0, i);
    std::string div2 = s.substr(i+1);

    if(div.empty())
        div = "-";
    
    if(div2.empty())
        div2 = "-";

    return s[i] + div + s[i] + div2;
}
int main() {
    auto candidate = f;
    assert(candidate(("kkxkxxfck")) == ("-kkxkxxfck"));
}
