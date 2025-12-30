#include "Util/immutable.h"
#include "Util/assert.h"

namespace cwerg {

const std::string_view kNames[] = {
    "Admiral", "Adobe",   "Albatross", "Alchemy",   "Alcohol",   "Alcove",
    "Alembic", "Alfalfa", "Algebra",   "Algorithm", "Alkali",    "Amber",
    "Aniline", "Apricot", "Arsenal",   "Artichoke", "Aubergine", "Assassin",
    "Average", "Azimuth", "Candy",     "Caravan",   "Caraway",   "Carob",
    "Cipher",  "Coffee",  "Cotton",    "Crimson"};

void Test() {
  ImmutablePool pool(4);
  for (const auto name : kNames) {
    const uint32_t pos = pool.Intern(name, 1);
    CHECK(pos != 0, "");
    CHECK(pos % 4 ==0, "");
    CHECK(name == pool.Data(pos), "");

    const uint32_t pos2 = pool.Intern(name, 1);
    CHECK(pos == pos2, "");
  }
}

void TestWithSizeInfo() {
  ImmutablePoolWithSizeInfo pool(4);
  for (const auto name : kNames) {
    const uint32_t pos = pool.Intern(name, 1);
    CHECK(pos != 0, "");
    CHECK(pos % 4 ==0, "");
    CHECK(name == pool.Data(pos), "");

    const uint32_t pos2 = pool.Intern(name, 1);
    CHECK(pos == pos2, "");
  }
}

}  // namespace cwerg

int main() {
  cwerg::Test();
  cwerg::TestWithSizeInfo();
  return 0;
}
