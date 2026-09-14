#include<assert.h>
#include<bits/stdc++.h>
std::string f(long integer, long n) {
    int i = 1;
    std::string text = std::to_string(integer);
    while (i + text.length() < n) {
        i += text.length();
    }
    return std::string(i + text.length() - text.length(), '0') + text;
}
int main() {
    auto candidate = f;
    assert(candidate((8999), (2)) == ("08999"));
}
