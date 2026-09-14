#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> places, std::vector<long> lazy) {
    std::sort(places.begin(), places.end());
    for (int l : lazy) {
        places.erase(std::remove(places.begin(), places.end(), l), places.end());
    }
    if (places.size() == 1) {
        return 1;
    }
    for (int i = 0; i < places.size(); ++i) {
        if (std::count(places.begin(), places.end(), places[i] + 1) == 0) {
            return i + 1;
        }
    }
    return places.size();
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)375, (long)564, (long)857, (long)90, (long)728, (long)92})), (std::vector<long>({(long)728}))) == (1));
}
