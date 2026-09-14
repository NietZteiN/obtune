#include<assert.h>
#include<bits/stdc++.h>
long f(std::string string) {
    try {
        return string.rfind('e');
    } catch (const std::exception& e) {
        return -1; // Assuming "Nuk" is meant to represent an error condition
    }
}
int main() {
    auto candidate = f;
    assert(candidate(("eeuseeeoehasa")) == (8));
}
