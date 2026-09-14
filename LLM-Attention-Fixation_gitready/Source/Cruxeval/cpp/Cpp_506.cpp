#include<assert.h>
#include<bits/stdc++.h>
std::string f(long n) {
    std::string p = "";
    if (n % 2 == 1) {
        p += "sn";
    } else {
        return std::to_string(n * n);
    }
    for (int x = 1; x <= n; x++) {
        if (x % 2 == 0) {
            p += "to";
        } else {
            p += "ts";
        }
    }
    return p;
}
int main() {
    auto candidate = f;
    assert(candidate((1)) == ("snts"));
}
