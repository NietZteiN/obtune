#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string text) {
    std::string res = "";
    
    for (char ch : text) {
        if (ch == 61) {
            break;
        }
        if (ch == 0) {
            continue;
        }
        res += std::to_string((int)ch) + "; ";
    }
    return "b'" + res + "'";
}
int main() {
    auto candidate = f;
    assert(candidate(("os||agx5")) == ("b'111; 115; 124; 124; 97; 103; 120; 53; '"));
}
