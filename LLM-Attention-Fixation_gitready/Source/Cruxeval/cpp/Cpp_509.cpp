#include<assert.h>
#include<bits/stdc++.h>
std::string f(long value, long width) {
    if (value >= 0) {
        return std::to_string(value).insert(0, width - std::to_string(value).length(), '0');
    }

    if (value < 0) {
        return "-" + std::to_string(-value).insert(1, width - std::to_string(-value).length(), '0');
    }
    return "";
}
int main() {
    auto candidate = f;
    assert(candidate((5), (1)) == ("5"));
}
