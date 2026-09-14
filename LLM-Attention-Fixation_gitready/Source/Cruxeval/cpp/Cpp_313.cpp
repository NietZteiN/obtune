#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, long l) {
    s.resize(l, '=');
    size_t pos = s.rfind('=');
    return s.substr(0, pos);
}
int main() {
    auto candidate = f;
    assert(candidate(("urecord"), (8)) == ("urecord"));
}
