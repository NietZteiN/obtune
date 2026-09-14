#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> years) {
    int a10 = std::count_if(years.begin(), years.end(), [](int x){return x <= 1900;});
    int a90 = std::count_if(years.begin(), years.end(), [](int x){return x > 1910;});

    if (a10 > 3) {
        return 3;
    } else if (a90 > 3) {
        return 1;
    } else {
        return 2;
    }
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1872, (long)1995, (long)1945}))) == (2));
}
