#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string, std::string sep) {
    int cnt = 0;
    for (size_t offset = string.find(sep); offset != std::string::npos;
         offset = string.find(sep, offset + sep.length()))
    {
        ++cnt;
    }
    std::string new_string = string + sep;
    for(int i=1; i<cnt; i++) {
        new_string += new_string;
    }
    std::reverse(new_string.begin(), new_string.end());
    return new_string;
}
int main() {
    auto candidate = f;
    assert(candidate(("caabcfcabfc"), ("ab")) == ("bacfbacfcbaacbacfbacfcbaac"));
}
