#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string field = text;
    std::string g = text;
    field.erase(std::remove(field.begin(), field.end(), ' '), field.end());
    std::replace(g.begin(), g.end(), '0', ' ');
    std::replace(text.begin(), text.end(), '1', 'i');

    return text;
}
int main() {
    auto candidate = f;
    assert(candidate(("00000000 00000000 01101100 01100101 01101110")) == ("00000000 00000000 0ii0ii00 0ii00i0i 0ii0iii0"));
}
