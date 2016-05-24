module Draft where
import Prelude hiding (length)
import qualified Data.List as L (genericLength, intersperse)
import Text.Printf

length = L.genericLength

{-

Background: we assume a population fullPop of fullN real agents. Each
agent is a record of type A with a few attributes (labels). Each
attribute can be classified into a few discrete ordered bins. A (1-D)
histogram is mapping from bins to (natural) numbers and from fullPop
we can easily compute a histogram for each attribute. It is also
straightforward to define 2-D (or n-D) histograms for pairs (or
n-tuples) of attributes. Part of the input for computing the synthetic
population is a collection of (mostly 1-D) histograms for a few
attributes of the full population. (But usually fullPop is not
available - only some histograms of fullPop.)

We also assume access to a subset ps of the population. This has
(normally all) data from someN real agents but usually someN << fullN.

The synthetic population is constructed to have
1. the same histograms as the full population and
2. similar correlations as the subset ps

Usually the synthetic population (with n attributes) is constructed in
three steps:

1. first an n-D histogram smallHist is contructed from the subset ps.
2. Then smallHist is scaled up to bigHist to match the collection of
   histograms for fullPop.
3. Finally a collection of individual agents are constructed to have
   bigHist as their n-D histogram.

-}


type Hist1 a    = a -> Count
type Hist2 a b  = a -> Hist1 b

histogram1 :: Eq a => (p -> a) -> Many p -> Hist1 a
histogram1 proj ps p = length (filter ((p==).proj) ps)

histogram2 :: (Eq a, Eq b) => (p -> a) -> (p -> b) -> Many p -> Hist2 a b
histogram2 proja projb ps a b = length (filter (\p -> a == proja p && b == projb p) ps)

hist2hista :: All b => Hist2 a b -> Hist1 a
hist2hista h2 = \a -> sumAll (\b -> h2 a b)

hist2histb :: All a => Hist2 a b -> Hist1 b
hist2histb h2 = \b -> sumAll (\a -> h2 a b)

-- Specification of the desired answer
checkSyntPopHist :: (All a, All b) => Hist1 a -> Hist1 b -> Hist2 a b -> Hist2 a b -> Bool
checkSyntPopHist ha hb smallHist bigHist =
     close epsilon ha (hist2hista bigHist) &&
     close epsilon hb (hist2histb bigHist) &&
     closeToProportional eps smallHist bigHist

-- ----------------------------------------------------------------

type Many = []
type Count = Double
  -- Integers works for counting, but when scaling up
  -- we will get to real numbers. Rationals can be
  -- used if we want to enable exact equality check.
-- type Count = Rational

eps = 1e-4
epsilon = 1e-9

sumAll :: (Bounded a, Enum a) => Hist1 a -> Count
sumAll   ha = sum (map    ha  [minBound .. maxBound])

sumMap :: (Bounded a, Enum a) => (Count -> Count) -> Hist1 a -> Count
sumMap f ha = sum (map (f.ha) [minBound .. maxBound])

class (Bounded a, Enum a) => All a

closeToProportional :: (All a, All b) => Count -> Hist2 a b -> Hist2 a b -> Bool
closeToProportional diff smallHist bigHist = undefined
  -- TODO: check that there is some scalar k such that  bigHist ~= k .* smallHist

close :: All a => Count -> Hist1 a -> Hist1 a -> Bool
close eps h1 h2 = sumMap (^2) (minus h1 h2) <= eps^2

minus :: Hist1 a -> Hist1 a -> Hist1 a
minus h1 h2 a = h1 a - h2 a

-- ----------------------------------------------------------------
-- Scaling

scale :: (All a, All b) => Hist1 a -> Hist1 b -> Hist2 a b -> Hist2 a b
scale ha hb = scaleCols hb . scaleRows ha

scaleRows :: All b => Hist1 a -> Hist2 a b -> Hist2 a b
scaleRows ha hab = \a -> scaleRow (ha a) (\b -> hab a b)

scaleRow :: All b => Count -> Hist1 b -> Hist1 b
scaleRow c hb = let s = sumAll hb
                    k = c / s
                in \b -> k * hb b

scaleCols :: All a => Hist1 b -> Hist2 a b -> Hist2 a b
scaleCols hb = transpose . scaleRows hb . transpose

-- Same as scaleRow
scaleCol :: All a => Count -> Hist1 a -> Hist1 a
scaleCol = scaleRow


transpose :: Hist2 a b -> Hist2 b a
transpose = flip

-- ----------------------------------------------------------------
-- Helper functions to print (rounded) histograms

showRound :: Count -> ShowS
showRound c = printf "%.0f%s" c
showRoundRat c = printf "%.0f%s" (fromRational c :: Double)

showHist' :: All a => (a -> ShowS) -> (Count -> ShowS) -> Hist1 a -> ShowS
showHist' sha shD ha = foldr (.) id
                         (L.intersperse (showString ", ")
                            (map (\a -> sha a . showString ": " . shD (ha a))
                                 [minBound .. maxBound]))

showHist :: (Show a, All a) => Hist1 a -> String
showHist ha = showHist' shows showRound ha ""

showHist2' :: (All a, All b) =>
  (a -> ShowS) -> (b -> ShowS) -> (Count -> ShowS) -> Hist2 a b -> ShowS
showHist2' sha shb shD hab =
  foldr (.) id
    (L.intersperse (showString ";\n")
       (map (\a -> sha a . showString ": {" . showHist' shb shD (hab a) . showString "}" )
           [minBound .. maxBound]))

showHist2 :: (Show a, Show b, All a, All b) => Hist2 a b -> String
showHist2 hab = showHist2' shows shows showRound hab ""
