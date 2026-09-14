#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s, long tab) {
    std::string result = s;
    std::string tabStr(tab, ' ');
    size_t pos = 0;
    while ((pos = result.find("\t", pos)) != std::string::npos) {
        result.replace(pos, 1, tabStr);
        pos += tab;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("Join us in Hungary"), (4)) == ("Join us in Hungary"));
}
