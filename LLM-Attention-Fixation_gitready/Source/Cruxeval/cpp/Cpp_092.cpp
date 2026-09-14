#include <cassert>
#include <string>
#include <algorithm>
#include <cctype>

bool f(std::string text) {
    return std::all_of(text.begin(), text.end(), [](unsigned char c) { return isascii(c); });
}
int main() {
    auto candidate = f;
    assert(candidate(("wW의IV]HDJjhgK[dGIUlVO@Ess$coZkBqu[Ct")) == (false));
}
