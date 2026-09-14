#include<assert.h>
#include<bits/stdc++.h>
bool f(long n) {
    std::string str_n = std::to_string(n);
    for (char c : str_n) {
        if (c < '0' || (c > '2' && c < '5') || c > '9') {
            return false;
        }
    }
    return true;
}
int main() {
    auto candidate = f;
    assert(candidate((1341240312)) == (false));
}
