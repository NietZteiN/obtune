#include<assert.h>
#include<bits/stdc++.h>
std::string f(long n) {
    std::string streak = "";
    for (char c : std::to_string(n)) {
        streak += c + std::string(c - '0', ' ');
    }
    return streak;
}
int main() {
    auto candidate = f;
    assert(candidate((1)) == ("1 "));
}
