#include<assert.h>
#include<bits/stdc++.h>
std::string f(long num) {
    if (0 < num && num < 1000 && num != 6174) {
        return "Half Life";
    }
    return "Not found";
}
int main() {
    auto candidate = f;
    assert(candidate((6173)) == ("Not found"));
}
